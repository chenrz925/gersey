from typing import Iterable

from prompt_toolkit.completion import Completer, CompleteEvent, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Filter

import jedi


class Python3Completer(Completer):
    def __init__(self):
        self.history = []

    def get_completions(
            self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        context = '\n'.join(self.history)
        context += ('\n' + document.text_before_cursor)
        script = jedi.Script(context)
        for completion in script.complete():
            text = completion.complete
            display = completion.name

            yield Completion(
                text=text,
                display=display,
                display_meta=completion.description
            )
