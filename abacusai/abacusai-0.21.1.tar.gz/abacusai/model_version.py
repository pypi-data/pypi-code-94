

class ModelVersion():
    '''
        A version of a model
    '''

    def __init__(self, client, modelVersion=None, status=None, modelId=None, modelConfig=None, trainingStartedAt=None, trainingCompletedAt=None, datasetVersions=None, error=None):
        self.client = client
        self.id = modelVersion
        self.model_version = modelVersion
        self.status = status
        self.model_id = modelId
        self.model_config = modelConfig
        self.training_started_at = trainingStartedAt
        self.training_completed_at = trainingCompletedAt
        self.dataset_versions = datasetVersions
        self.error = error

    def __repr__(self):
        return f"ModelVersion(model_version={repr(self.model_version)}, status={repr(self.status)}, model_id={repr(self.model_id)}, model_config={repr(self.model_config)}, training_started_at={repr(self.training_started_at)}, training_completed_at={repr(self.training_completed_at)}, dataset_versions={repr(self.dataset_versions)}, error={repr(self.error)})"

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.id == other.id

    def to_dict(self):
        return {'model_version': self.model_version, 'status': self.status, 'model_id': self.model_id, 'model_config': self.model_config, 'training_started_at': self.training_started_at, 'training_completed_at': self.training_completed_at, 'dataset_versions': self.dataset_versions, 'error': self.error}

    def delete(self):
        return self.client.delete_model_version(self.model_version, model_version)

    def wait_for_training(self, timeout=None):
        return self.client._poll(self, {'PENDING', 'TRAINING'}, delay=30, timeout=timeout)

    def get_status(self):
        return self.describe().status
