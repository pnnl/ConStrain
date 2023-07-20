import json
from collections import defaultdict

class Workflow():
    def __init__(self, workflow):
        self.workflow = workflow

class State():
    def __init__(self, state):  
        self.state = defaultdict()

        if isinstance(state, str):
            try:
                unformmated_state = json.loads(state)
            except json.decoder.JSONDecodeError:
                raise ValueError('Invalid JSON')
            
            state_title = next(iter(unformmated_state))
            self.state.update(unformmated_state[state_title])
            self.state['Title'] = state_title
        elif isinstance(state, dict):
            self.state.update(state)
            

    def set_state(self, state):
        self.state = state

    def check_state(self, state):
        viable = True

        def error():
            raise ValueError('Invalid JSON')

        if isinstance(state, str):
            try:
                uf_state = json.loads(state)
                if uf_state.keys() > 1:
                    error()
            except json.decoder.JSONDecodeError:
                error()

            state_title = next(iter(uf_state))
            self.state.update(uf_state[state_title])
            self.state['Title'] = state_title

        state_type = self.state['Type']
        if state_type is None:
            error()
        elif state_type == 'MethodCall':
            if not state['MethodCall']:
                error()
        elif state_type == 'Choice':
            if not state['Choices']:
                error()
            else:
                if not isinstance(self.state['Choices'], list):
                    error()


            
