from krita import DockWidgetFactory, DockWidgetFactoryBase
from .ChallengePromptMaker import ChallengePromptMaker


DOCKER_NAME = 'ChallengePromptMaker'
DOCKER_ID = 'pykrita_ChallengePromptMaker'


Application.addDockWidgetFactory(
    DockWidgetFactory(DOCKER_ID, DockWidgetFactoryBase.DockPosition.DockRight,
        ChallengePromptMaker))
