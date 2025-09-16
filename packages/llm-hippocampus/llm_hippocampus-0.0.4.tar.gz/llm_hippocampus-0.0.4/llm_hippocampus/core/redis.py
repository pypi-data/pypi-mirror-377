# -*- coding: utf-8 -*-
from redis import Redis
from redis.commands.search.query import Query
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from llm_hippocampus.core.utils import list2np_array
from .logger import logger
from .. import env
from itertools import groupby
from csv import reader

def client(url):
    try_time = 0
    client = None
    while try_time < 3:
        logger.info(f"尝试获取Redis客户端，第{try_time}次")
        try:
            client = Redis.from_url(
                url,
                decode_responses=True,
                encoding='utf-8',
            )
            break
        except Exception as e:
            err_msg = f"获取Redis客户端失败:， 错误信息：{e}"
            logger.error(err_msg)
            try_time += 1

    if client is None:
        raise err_msg

    return client

def create_search_index(client: Redis, schema: dict | str, overwrite: bool = True) -> SearchIndex:
    try:
        logger.info(f"创建索引，索引信息：{schema}")
        if isinstance(schema, str):
            index = SearchIndex.from_yaml(schema, redis_client=client, validate_on_load=True)
        else:
            index = SearchIndex.from_dict(schema, redis_client=client, validate_on_load=True)
        index.create(overwrite=overwrite)
    except Exception as e:
        logger.error(f"创建索引失败，索引信息：{schema}，错误信息：{e}")
        raise e
    return index

def load_data2search_index(index: SearchIndex, data: list, id_field: str = None):
    try:
        logger.info(f"加载数据到索引，索引信息：{index}，数据量：{len(data)}")
        if id_field:
            keys = index.load(data, id_field=id_field)
        else:
            keys = index.load(data)
    except Exception as e:
        logger.error(f"加载数据到索引失败，索引信息：{index}，数据量：{len(data)}，错误信息：{e}")
        raise e
    return keys

def delete4search_index(index: SearchIndex, keys):
    try:
        logger.info(f"删除数据到索引，索引信息：{index}，数据量：{len(keys)}")
        index.drop_keys(keys)
    except Exception as e:
        logger.error(f"删除数据到索引失败，索引信息：{index}，数据量：{len(keys)}，错误信息：{e}")
        raise e

def vector_query(query: str, index: SearchIndex, embedding, schema = None, **kwargs):
    try:
        distance_threshold = kwargs.get('distance_threshold', env.DISTANCE_THRESHOLD)
        precision = kwargs.get('precision', 'float32')
        dims = kwargs.get('dims', 768)
        vector_field_name = kwargs.get('vector_field_name')

        if not embedding:
            raise ValueError("embedding不能为空")

        if not query:
            raise ValueError("query不能为空")

        if not vector_field_name:
            raise ValueError("vector_field_name不能为空")

        default_fields = []
        if schema:
            for field in schema['fields']:
                default_fields.append(field['name'])

        vquery = VectorQuery(
            vector=list2np_array(embedding.encode(query, precision=precision, truncate_dim=dims)).tobytes(),
            vector_field_name=vector_field_name,
        )

        filter_expression = kwargs.get('filter_expression', '')
        if filter_expression:
            vquery._filter_expression = filter_expression

        return_fileds = kwargs.get('return_fileds', default_fields)
        if return_fileds:
            vquery.return_fields(*return_fileds)

        top_k = kwargs.get('top_k', env.TOP_K)

        if top_k > 0:
            vquery._num_results = top_k

        sort_by = kwargs.get('sort_by')
        if sort_by:
            vquery.sort_by(sort_by)

        results = index.query(vquery)
        filter_results = []
        if distance_threshold and len(results) > 0:
            for rs in results:
                vd = float(rs.get('vector_distance'))
                if vd <= distance_threshold:
                    filter_results.append(rs)
            results = filter_results

        return results

    except Exception as e:
        logger.error(f"查询数据失败，错误信息：{e}")
        raise e

def add(client: Redis, key, value, expire_time=env.SHORT_TERM_MEMORY_ACTIVE_TIME):
    try:
        logger.debug(f"添加键值对[{key}]，值长度：{len(value)}，生效时间：{expire_time}s")
        client.set(key, value, ex=expire_time)
    except Exception as e:
        logger.error(f"添加键值对失败，错误信息：{e}")
        raise e

def add_items(client: Redis, items, expire_time=env.SHORT_TERM_MEMORY_ACTIVE_TIME):
    try:
        logger.debug(f"添加键值对列表，数据量：{len(items)}，生效时间：{expire_time}s")
        if len(items) > 5:
            pipline = client.pipeline()
            for item in items:
                if not isinstance(item, dict):
                    err_msg = f"添加项必须为字典"
                    logger.error(err_msg)
                    raise err_msg
                pipline.hmset(item["id"], item, ex=expire_time)
            pipline.execute()
        else:
            for item in items:
                client.hmset(item['id'], item, ex=expire_time)
    except Exception as e:
        logger.error(f"添加键值对失败，错误信息：{e}")
        raise e

def remove(client: Redis, item_keys):
    try:
        logger.debug(f"删除键值对列表，键列表：{item_keys}")
        if len(item_keys) > 5:
            pipline = client.pipeline()
            for item_key in item_keys:
                pipline.delete(item_key)
            pipline.execute()
        else:
            for item_key in item_keys:
                client.delete(item_key)
    except Exception as e:
        logger.error(f"删除键值对失败，错误信息：{e}")
        raise e

def replace(client: Redis, items):
    try:
        logger.debug(f"替换键值对列表，数据量：{len(items)}")
        if len(items) > 5:
            pipline = client.pipeline()
            for item in items:
                pipline.set(item['id'], item)
            pipline.execute()
        else:
            for item in items:
                client.set(item['id'], item)
    except Exception as e:
        logger.error(f"替换键值对失败，错误信息：{e}")
        raise e

def get(client: Redis, item_key):
    try:
        logger.debug(f"获取键值对[{item_key}]")
        return client.get(item_key)
    except Exception as e:
        logger.error(f"获取键值对失败，错误信息：{e}")

def get_keys(client: Redis, start=0, count=20, match='*'):
    try:
        logger.debug(f"获取键列表，start：{start}，count：{count}，match：{match}")
        keys_list = client.scan(start, count=count, match=match)
        return keys_list
    except Exception as e:
        logger.error(f"获取键列表失败，错误信息：{e}")
        return None

def search(client: Redis, model, query, top_k=10):
    try:
        logger.debug(f"搜索，query：{query}，top_k：{top_k}")
        query_embedding = model.encode(query).astype("float32").tobytes()
        q = Query(f"*=>[KNN {top_k} @embedding $vec_param AS vector_score]") \
            .sort_by("vector_score") \
            .return_fields("content", "genre", "vector_score") \
            .params({"vec_param": query_embedding})
        res = client.ft("vector_idx").search(q)
        return res
    except Exception as e:
        logger.error(f"搜索失败，错误信息：{e}")
        raise e

def load_set(client: Redis, key, IN, **kwargs):
    """
    """
    try:
        logger.debug(f"加载集合，key：{key}，数据量：{len(IN)}")
        r = client
        pipeline_redis = r.pipeline()
        count = 0
        #batch_size = kwargs['batch_size']
        batch_size = kwargs.get('batch_size', 1000)

        seen = set([None])
        for member, _ in groupby(reader(IN, delimiter='\t'),
                                lambda x: x[0] if len(x) else None):
            if member not in seen:
                pipeline_redis.sadd(key, member.rstrip())
                count += 1
            seen.add(member)
            if not count % batch_size:
                pipeline_redis.execute()
        #send the last batch
        pipeline_redis.execute()
    except Exception as e:
        logger.error(f"加载集合失败，错误信息：{e}")
        raise e


def load_list(client: Redis, key, IN, **kwargs):
    """
    """
    try:
        logger.debug(f"加载列表，key：{key}，数据量：{len(IN)}")
        r = client
        pipeline_redis = r.pipeline()
        count = 0
        batch_size = kwargs.get('batch_size', 1000)

        for line in IN:
            pipeline_redis.rpush(key, line.rstrip())
            count += 1
            if not count % batch_size:
                pipeline_redis.execute()
        #send the last batch
        pipeline_redis.execute()
    except Exception as e:
        logger.error(f"加载列表失败，错误信息：{e}")
        raise e


def load_hash_list(client: Redis, IN, **kwargs):
    """
    """
    try:
        logger.debug(f"加载哈希列表，数据量：{len(IN)}")
        r = client
        pipeline_redis = r.pipeline()
        count = 0
        batch_size = kwargs.get('batch_size', 1000)

        for key, mapping in IN:
            pipeline_redis.hmset(key, mapping)
            count += 1
            if not count % batch_size:
                pipeline_redis.execute()
        #send the last batch
        pipeline_redis.execute()
    except Exception as e:
        logger.error(f"加载哈希列表失败，错误信息：{e}")
        raise e

if __name__ == '__main__':
    pass
