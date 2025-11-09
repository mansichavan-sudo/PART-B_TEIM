from celery import shared_task
from .utils import train_content_model, train_cf_svd

@shared_task
def retrain_recommenders():
    # retrain both models
    train_content_model()
    train_cf_svd()
    return "retrained"
