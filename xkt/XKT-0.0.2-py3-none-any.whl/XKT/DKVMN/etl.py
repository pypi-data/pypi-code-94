# coding: utf-8
# 2021/8/22 @ tongshiwei

import mxnet.ndarray as nd
from tqdm import tqdm
from XKT.utils import extract
from baize.utils import FixedBucketSampler, PadSequence


def transform(raw_data, batch_size, num_buckets=100):
    # 定义数据转换接口
    # raw_data --> batch_data

    responses = raw_data

    batch_idxes = FixedBucketSampler([len(rs) for rs in responses], batch_size, num_buckets=num_buckets)
    batch = []

    def response_index(r):
        correct = 0 if r[1] <= 0 else 1
        return r[0] * 2 + correct

    def question_index(r):
        return r[0]

    for batch_idx in tqdm(batch_idxes, "batchify"):
        batch_qs = []
        batch_rs = []
        batch_labels = []
        for idx in batch_idx:
            batch_qs.append([question_index(r) for r in responses[idx]])
            batch_rs.append([response_index(r) for r in responses[idx]])
            labels = [0 if r[1] <= 0 else 1 for r in responses[idx][:]]
            batch_labels.append(list(labels))

        max_len = max([len(rs) for rs in batch_rs])
        padder = PadSequence(max_len, pad_val=0)
        batch_qs, _ = zip(*[(padder(qs), len(qs)) for qs in batch_qs])
        batch_rs, data_mask = zip(*[(padder(rs), len(rs)) for rs in batch_rs])

        max_len = max([len(rs) for rs in batch_labels])
        padder = PadSequence(max_len, pad_val=0)
        batch_labels, label_mask = zip(*[(padder(labels), len(labels)) for labels in batch_labels])
        batch.append(
            [
                nd.array(batch_qs, dtype="float32"),
                nd.array(batch_rs, dtype="float32"),
                nd.array(data_mask),
                nd.array(batch_labels),
                nd.array(label_mask)
            ]
        )

    return batch


def etl(data_src, cfg=None, batch_size=None, **kwargs):  # pragma: no cover
    batch_size = batch_size if batch_size is not None else cfg.batch_size
    raw_data = extract(data_src)
    return transform(raw_data, batch_size, **kwargs)
