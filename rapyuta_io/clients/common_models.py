import rapyuta_io
from rapyuta_io.utils.object_converter import ObjBase, enum_field
import six
from rapyuta_io.utils.error import InvalidParameterException
from rapyuta_io.utils import ObjDict


class InternalDeploymentStatus(ObjBase):
    """
    InternalDeploymentStatus represents Internal Deployment Status.

    :ivar phase: phase of the internal deployment
    :vartype phase: :py:class:`rapyuta_io.clients.deployment.DeploymentPhaseConstants`
    :ivar status: (full-only) status of the internal deployment
    :vartype status: :py:class:`rapyuta_io.clients.deployment.DeploymentStatusConstants`
    :ivar error_code: error code of the internal deployment
    :vartype error_code: list(str)

    :param phase: phase of the internal deployment
    :type phase: :py:class:`rapyuta_io.clients.deployment.DeploymentPhaseConstants`
    :param status: status of the internal deployment
    :type status: :py:class:`rapyuta_io.clients.deployment.DeploymentStatusConstants`
    :param error_code: error code of the internal deployment
    :type error_code: list(str)
    """

    def __init__(self, phase, status=None, error_code=None):
        self.phase = phase
        self.status = status
        self.error_code = error_code

    def get_deserialize_map(self):
        return {
            'phase': enum_field('phase', rapyuta_io.DeploymentPhaseConstants),
            'status': enum_field('status', rapyuta_io.DeploymentStatusConstants),
            'error_code': 'error_code'
        }

    def get_serialize_map(self):
        return {}


class Limits(ObjDict, ObjBase):
    """
    Limits represent the cpu and memory specs of a cloud network

    :ivar cpu: cpu
    :vartype cpu: Union [float, integer]
    :ivar memory: memory
    :vartype memory: integer

    :param cpu: cpu
    :type cpu: Union [float, integer]
    :param memory: memory
    :type memory: integer
    """

    def __init__(self, cpu, memory):
        self.validate(cpu, memory)
        super(ObjDict, self).__init__(cpu=cpu, memory=memory)

    @staticmethod
    def validate(cpu, memory):
        if not isinstance(cpu, float) and not isinstance(cpu, six.integer_types):
            raise InvalidParameterException('cpu must be a float or integer')
        if cpu <= 0:
            raise InvalidParameterException('cpu must be a positive number')
        if not isinstance(memory, six.integer_types) or memory <= 0:
            raise InvalidParameterException('memory must be a positive integer')

    def get_deserialize_map(self):
        return {
            'cpu': 'cpu',
            'memory': 'memory',
        }

    def get_serialize_map(self):
        return {
            'cpu': 'cpu',
            'memory': 'memory',
        }
