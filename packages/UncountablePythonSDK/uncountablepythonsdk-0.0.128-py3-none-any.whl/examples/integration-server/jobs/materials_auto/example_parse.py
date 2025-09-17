from dataclasses import dataclass

from uncountable.integration.job import JobArguments, WebhookJob, register_job
from uncountable.types import (
    base_t,
    generic_upload_t,
    identifier_t,
    job_definition_t,
    uploader_t,
)


@dataclass(kw_only=True)
class ParsePayload:
    async_job_id: base_t.ObjectId


@register_job
class ParseExample(WebhookJob[ParsePayload]):
    def run(
        self, args: JobArguments, payload: ParsePayload
    ) -> job_definition_t.JobResult:
        dummy_parsed_file_data: list[uploader_t.ParsedFileData] = [
            uploader_t.ParsedFileData(
                file_name="my_file_to_upload.xlsx",
                file_structures=[
                    uploader_t.DataChannel(
                        type=uploader_t.StructureElementType.CHANNEL,
                        channel=uploader_t.TextChannelData(
                            name="column1",
                            type=uploader_t.ChannelType.TEXT_CHANNEL,
                            data=[
                                uploader_t.StringValue(value="value1"),
                                uploader_t.StringValue(value="value4"),
                                uploader_t.StringValue(value="value7"),
                            ],
                        ),
                    ),
                    uploader_t.DataChannel(
                        type=uploader_t.StructureElementType.CHANNEL,
                        channel=uploader_t.TextChannelData(
                            name="column2",
                            type=uploader_t.ChannelType.TEXT_CHANNEL,
                            data=[
                                uploader_t.StringValue(value="value2"),
                                uploader_t.StringValue(value="value5"),
                                uploader_t.StringValue(value="value8"),
                            ],
                        ),
                    ),
                    uploader_t.DataChannel(
                        type=uploader_t.StructureElementType.CHANNEL,
                        channel=uploader_t.TextChannelData(
                            name="column3",
                            type=uploader_t.ChannelType.TEXT_CHANNEL,
                            data=[
                                uploader_t.StringValue(value="value3"),
                                uploader_t.StringValue(value="value6"),
                                uploader_t.StringValue(value="value9"),
                            ],
                        ),
                    ),
                    uploader_t.HeaderEntry(
                        type=uploader_t.StructureElementType.HEADER,
                        value=uploader_t.TextHeaderData(
                            name="file_source",
                            type=uploader_t.HeaderType.TEXT_HEADER,
                            data=uploader_t.StringValue(value="my_file_to_upload.xlsx"),
                        ),
                    ),
                ],
            )
        ]

        args.client.complete_async_parse(
            parsed_file_data=dummy_parsed_file_data,
            async_job_key=identifier_t.IdentifierKeyId(id=payload.async_job_id),
            upload_destination=generic_upload_t.UploadDestinationRecipe(
                recipe_key=identifier_t.IdentifierKeyId(id=1)
            ),
        )

        return job_definition_t.JobResult(success=True)

    @property
    def webhook_payload_type(self) -> type:
        return ParsePayload
