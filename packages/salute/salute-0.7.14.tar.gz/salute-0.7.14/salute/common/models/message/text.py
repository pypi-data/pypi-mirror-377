from typing import Annotated

from pydantic import BaseModel, StringConstraints

from salute.common.models.message.entities import Entities

LowerCaseText = Annotated[str | None, StringConstraints(to_lower=True)]

class Text(BaseModel):
    original_text: LowerCaseText = ""
    normalized_text: LowerCaseText = ""
    human_normalized_text: LowerCaseText = ""
    asr_normalized_message: LowerCaseText = ""
    human_normalized_text_with_anaphora: LowerCaseText = ""
    entities: Entities = Entities()

    def get_number(self) -> int | None:
        value = None

        if len(self.entities.NUM_TOKEN):
            data = self.entities.NUM_TOKEN[0]

            if type(data) is dict and data.get("value"):
                value = data["value"]

        if value is None:
            return None

        try:
            float(value)
            return int(value)
        except ValueError:
            return None
