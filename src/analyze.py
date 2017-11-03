import boto3
from easydict import EasyDict as ed

config = ed(
    region_name = 'us-west-2',
    s3_bucket_name = 'steem-hackaton-input'
)

rkg = boto3.client('rekognition', region_name=config.region_name)


def nsfw(img: bytes):
    response = rkg.detect_moderation_labels(
        Image={'Bytes': img},
    )
    return response['ModerationLabels']

def labels(img: bytes):
    response = rkg.detect_labels(
        Image={'Bytes': img},
        MaxLabels=100,
        MinConfidence=80,
    )
    return response['Labels']
