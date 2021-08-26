import json
import logging
from asyncio import sleep
from copy import copy
from datetime import datetime
from typing import Any, Dict, List, Text, Tuple

from prettytable import PrettyTable
from rich.console import Console
from rich.progress import track
from rich.table import Table

from neuralspace.apis import get_async_http_session
from neuralspace.constants import (
    AUTHORIZATION,
    COMMON_HEADERS,
    COMPLETED,
    COUNT,
    DATA,
    DEAD,
    ENTITIES,
    ENTITY_ACC,
    EXAMPLE,
    EXAMPLE_ID,
    EXAMPLES,
    FAILED,
    FILTER,
    INTENT,
    INTENT_ACCURACY,
    INTENT_CLASSIFIER_METRICS,
    LANGUAGE,
    LANGUAGES,
    LAST_STATUS_UPDATED,
    METRICS,
    MODEL_ID,
    MODEL_NAME,
    MODELS,
    N_REPLICAS,
    NER_METRICS,
    NUMBER_OF_EXAMPLES,
    NUMBER_OF_INTENTS,
    NUMBER_OF_MODELS,
    PAGE_NUMBER,
    PAGE_SIZE,
    PREPARED,
    PROJECT_ID,
    PROJECT_NAME,
    PROJECTS,
    REPLICAS,
    SEARCH,
    TEXT,
    TIMED_OUT,
    TRAINING_STATUS,
    TRAINING_TIME,
    TYPE,
    neuralspace_url, UPLOAD_DATASET_COMMAND, INITIATED, QUEUED, START_INDEX, END_INDEX,
)
from neuralspace.nlu.constants import (
    CREATE_EXAMPLE_URL,
    CREATE_PROJECT_URL,
    DELETE_EXAMPLE_URL,
    DELETE_MODELS_URL,
    DELETE_PROJECT_URL,
    DEPLOY_MODEL_URL,
    LANGUAGE_CATALOG_URL,
    LIST_EXAMPLES_URL,
    LIST_MODELS_URL,
    LIST_PROJECTS_URL,
    PARSE_URL,
    SINGLE_MODEL_DETAILS_URL,
    TRAIN_MODEL_URL, C_COMPLETED, C_QUEUED, C_INITIATED, C_DEAD, C_TIMED_OUT, C_FAILED,
)
from neuralspace.utils import get_auth_token, is_success_status, print_ner_response

logger = logging.getLogger(__name__)
console = Console()


async def get_languages() -> Dict[Text, Any]:
    logger.debug("Fetching all supported languages for NLU")
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().get(
        url=f"{neuralspace_url()}/{LANGUAGE_CATALOG_URL}",
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            logger.debug("Successfully created project")
            logger.info(f"{json.dumps(json_response, indent=4)}")
        else:
            logger.error("Failed to create project")
            logger.error(f"Platform response: \n {json.dumps(json_response, indent=4)}")
    return json_response


async def create_project(project_name: Text, languages: List[Text]) -> Dict[Text, Any]:
    console.print(
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] Creating a project called "
        f"{project_name} in languages: {', '.join(languages)}!"
    )
    payload = {PROJECT_NAME: project_name, LANGUAGE: languages}
    HEADERS = copy(COMMON_HEADERS)
    table = Table()
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{CREATE_PROJECT_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            console.print(
                "> [deep_sky_blue2]INFO[/deep_sky_blue2]"
                " 🗝 Retrieving credentials from config..."
            )
            console.print(
                "> [deep_sky_blue2]INFO[/deep_sky_blue2] "
                "✅ Successfully created project!"
            )
            console.print(
                "> [deep_sky_blue2]INFO[/deep_sky_blue2] "
                "Here 💁 is your project information..."
            )
            table.add_column("Name")
            table.add_column("Language")
            table.add_column("App Type")
            table.add_column("Project Id", style="green")
            language_to_write = ""
            for i, language in enumerate(json_response[DATA]["language"]):
                if i == len(json_response[DATA]["language"]) - 1:
                    language_to_write += language
                else:
                    language_to_write += language + ", "
            table.add_row(
                json_response[DATA]["projectName"],
                language_to_write,
                json_response[DATA]["appType"],
                json_response[DATA]["projectId"],
            )
            console.print(table)
            console.print(
                f"⏩ Upload data to your project using this command:"
                f" [dark_orange3]{UPLOAD_DATASET_COMMAND}[/dark_orange3]"
            )
        else:
            console.print("> [red]ERROR[/red] Failed ❌  to create project")
            console.print(f"> 😔[red]{json_response[DATA]['error']}[/red]")
    return json_response


async def delete_project(project_id: Text) -> Dict[Text, Any]:
    logger.info(f"Deleting project with id: {project_id}")
    payload = {PROJECT_ID: project_id}
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().delete(
        url=f"{neuralspace_url()}/{DELETE_PROJECT_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            logger.info(f"Platform Response: \n{json.dumps(json_response, indent=4)}")
        else:
            logger.error("Failed to delete projects")
            logger.error(f"Platform response: \n {json.dumps(json_response, indent=4)}")
    return json_response


def print_projects_table(projects: Dict[Text, Any]):
    table = Table(show_header=True, header_style="bold #c47900", show_lines=True)
    table.add_column("Project Name", style="#c47900")
    table.add_column("Project ID", style="#c47900")
    table.add_column("Number of Examples", style="#c47900")
    table.add_column("Number of Intents", style="#c47900")
    table.add_column("Number of Models", style="#c47900")
    table.add_column("Languages", style="#c47900")
    for data in projects[DATA][PROJECTS]:
        table.add_row(
                data[PROJECT_NAME],
                data[PROJECT_ID],
                data[NUMBER_OF_EXAMPLES],
                data[NUMBER_OF_INTENTS],
                data[NUMBER_OF_MODELS],
                data[LANGUAGE]
        )
    console.print(table)


def train_table(projects: Dict[Text, Any]):
    table = PrettyTable()
    table.field_names = [
        "Project Name",
        "Project ID",
        "Number of Examples",
        "Number of Intents",
        "number of Models",
        "Languages",
    ]
    for data in projects[DATA][PROJECTS]:
        table.add_row(
            [
                data[PROJECT_NAME],
                data[PROJECT_ID],
                data[NUMBER_OF_EXAMPLES],
                data[NUMBER_OF_INTENTS],
                data[NUMBER_OF_MODELS],
                data[LANGUAGE],
            ]
        )
    logger.info(f"\n{table}")


async def list_projects(
    search: Text, page_size: int, page_number: int, languages: List[Text]
) -> Dict[Text, Any]:
    payload = {
        SEARCH: search,
        PAGE_NUMBER: page_number,
        PAGE_SIZE: page_size,
        LANGUAGES: languages,
    }
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{LIST_PROJECTS_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            console.print(
                f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 📚 Your projects for Page {page_number} with Page Size: {page_size}"
            )
            print_projects_table(json_response)
        else:
            console.print("> [red]ERROR[/red] ❌ Failed to list projects")
            console.print(f"Platform response: \n{json.dumps(json_response, indent=4)}")
    return json_response


def print_examples_table(examples: Dict[Text, Any]):
    table = Table(show_header=True, header_style="bold #c47900", show_lines=True)
    table.add_column("Example ID", style="#c47900")
    table.add_column("Text", style="#c47900")
    table.add_column("Intent", style="#c47900")
    table.add_column("N Entities", style="#c47900")

    logger.info(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 🔢 Total Examples Count: {examples[DATA][COUNT]}")
    for data in examples[DATA][EXAMPLES]:
        text = data[TEXT][:20]
        if len(data[TEXT]) > 20:
            text = f"{text}..."
        table.add_row(data[EXAMPLE_ID], text, data[INTENT], len(data[ENTITIES]))

    console.print(table)


async def list_examples(
    project_id: Text,
    language: Text,
    prepared: bool,
    type: Text,
    intent: Text,
    page_number: int,
    page_size: int,
) -> Dict[Text, Any]:
    console.print(
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] ⬇️ Fetching Examples with filter: \n"
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] #️⃣ [bold]Project ID:[/bold] [orange]{project_id}[orange]"
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] ✏️ Language: {language}; "
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 🍲 Prepared: {prepared}; "
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 📌 type: {type}"
    )
    payload = {
        FILTER: {
            PROJECT_ID: project_id,
            LANGUAGE: language,
            PREPARED: prepared,
            TYPE: type,
        },
        PAGE_NUMBER: page_number,
        PAGE_SIZE: page_size,
    }
    if intent:
        payload[FILTER][INTENT] = intent

    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{LIST_EXAMPLES_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            print_examples_table(json_response)
        else:
            console.print("> [red]ERROR[/red] ❌ Failed to list examples")
            console.print(f"> Platform response: \n{json.dumps(json_response, indent=4)}")
    return json_response


def get_training_status_colour(status: Text) -> Text:
    if status == COMPLETED:
        return C_COMPLETED
    elif status == FAILED:
        return C_FAILED
    elif status == TIMED_OUT:
        return C_TIMED_OUT
    elif status == DEAD:
        return C_DEAD
    elif status == INITIATED:
        return C_INITIATED
    elif status == QUEUED:
        return C_QUEUED


def print_models_table(models: Dict[Text, Any]):
    table = Table(show_header=True, header_style="bold #c47900", show_lines=True)
    table.add_column("Model ID", style="#c47900")
    table.add_column("Model Name", style="#c47900")
    table.add_column("Training Status", style="#c47900")
    table.add_column("Intent Acc", style="#c47900")
    table.add_column("Entity Acc", style="#c47900")
    table.add_column("Training Time (sec)", style="#c47900")
    table.add_column("Last Updated", style="#c47900")

    console.print(f"> Total Models Count: {models[DATA][COUNT]}")
    logger.info(f" [deep_sky_blue2]INFO[/deep_sky_blue2] 🔢 Total Models Count: {models[DATA][COUNT]}")
    for data in models[DATA][MODELS]:
        table.add_row(

                data[MODEL_ID],
                data[MODEL_NAME],
                f"{get_training_status_colour(data[TRAINING_STATUS])} {data[TRAINING_STATUS]}",
                data[REPLICAS],
                "{:.3f}".format(
                    data[METRICS][INTENT_CLASSIFIER_METRICS][INTENT_ACCURACY]
                )
                if data[TRAINING_STATUS] == COMPLETED
                else 0.0,
                "{:.3f}".format(data[METRICS][NER_METRICS][ENTITY_ACC])
                if data[TRAINING_STATUS] == COMPLETED
                else 0.0,
                data[TRAINING_TIME] if data[TRAINING_STATUS] == COMPLETED else 0.0,
                data[LAST_STATUS_UPDATED],

        )
    console.print(table)


async def list_models(
    project_id: Text,
    language: Text,
    training_status: List[Text],
    page_number: int,
    page_size: int,
) -> Dict[Text, Any]:
    console.print(
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] ⬇️ Fetching models with filter: \n"
        f"#️⃣ Project ID: {project_id}; "
        f"✏️ Language: {language}; "
        f"🏋️ Training Statuses: {training_status}"
    )
    payload = {
        FILTER: {PROJECT_ID: project_id, LANGUAGE: language},
        PAGE_NUMBER: page_number,
        PAGE_SIZE: page_size,
    }
    if training_status:
        payload[FILTER][TRAINING_STATUS] = training_status

    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{LIST_MODELS_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            print_models_table(json_response)
        else:
            logger.error("> [red]ERROR[/red] ❌ Failed to list models")
            logger.error(f"> Platform response: \n{json.dumps(json_response, indent=4)}")
    return json_response


async def delete_examples(example_ids: List[Text]) -> Dict[Text, Any]:
    console.print(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 🗑️ Deleting Example with id: {example_ids}")
    payload = {EXAMPLE_ID: example_ids}
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().delete(
        url=f"{neuralspace_url()}/{DELETE_EXAMPLE_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            console.print("> [deep_sky_blue2]INFO[/deep_sky_blue2] ✅ Successfully deleted example!")
        else:
            logger.error("> [red]ERROR[/red] ❌ Failed to delete examples")
            logger.error(f"> Platform response: \n{json.dumps(json_response, indent=4)}")
    return json_response


async def upload_dataset(
    nlu_data: List[Dict[Text, Text]],
    project_id: Text,
    language: Text,
    skip_first: int = 0,
    ignore_errors: bool = False,
) -> List[Dict[Text, Any]]:
    responses = []
    error_examples = []
    console.print(
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] Uploading {len(nlu_data) - skip_first} "
        f"examples for project {project_id} and language {language}"
    )
    console.print(
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] Skipping first {skip_first} examples"
    )
    for chunk_id, example in track(
        enumerate(nlu_data[skip_first:]),
        description="[bold orange4]uploading[/bold orange4]...",
        total=len(
            nlu_data[skip_first:],
        ),
    ):
        batch = {PROJECT_ID: project_id, LANGUAGE: language, EXAMPLE: example}
        HEADERS = copy(COMMON_HEADERS)
        HEADERS[AUTHORIZATION] = get_auth_token()
        async with get_async_http_session().post(
            url=f"{neuralspace_url()}/{CREATE_EXAMPLE_URL}",
            data=json.dumps(batch, ensure_ascii=False),
            headers=HEADERS,
        ) as response:
            json_response = await response.json(encoding="utf-8")
            if is_success_status(response.status):
                responses.append(json_response)
            else:
                console.print(f"> [red]ERROR[/red] ❌ Failed to upload example with text [dark_orange3]{example['text']}[/dark_orange3]")
                console.print(
                    f"> Failed on example: \n{json.dumps(example, indent=4, ensure_ascii=False)}"
                )
                console.print(
                    f"> Platform response: \n{json.dumps(json_response, indent=4)}"
                )
                error_examples.append(example)
                if ignore_errors:
                    continue
                else:
                    break
    console.print(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] ✅ Uploaded {len(responses)} examples")
    console.print(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] ❌ Failed on {len(error_examples)} examples")
    with open("failed_examples.json", "w") as f:
        json.dump(error_examples, f, ensure_ascii=False)
        console.print("> [deep_sky_blue2]INFO[/deep_sky_blue2] ✍️ Writing failed examples into failed_examples.json")
    return responses


async def wait_till_training_completes(
    model_id: Text, wait: bool, wait_interval: int
) -> Dict[Text, Any]:
    if wait:
        payload = {
            MODEL_ID: model_id,
        }
        HEADERS = copy(COMMON_HEADERS)
        HEADERS[AUTHORIZATION] = get_auth_token()
        console.print(
            f"> [deep_sky_blue2]INFO[/deep_sky_blue2] ⏳ Waiting for training job to "
            f"get trained for model id: {model_id}"
        )
        current_status = ""
        with console.status("...") as status:
            while True:
                async with get_async_http_session().get(
                    url=f"{neuralspace_url()}/{SINGLE_MODEL_DETAILS_URL}",
                    params=payload,
                    headers=HEADERS,
                ) as response:
                    json_response = await response.json(encoding="utf-8")
                    if is_success_status(response.status):
                        current_status = json_response[DATA][TRAINING_STATUS]
                        if (
                            json_response[DATA][TRAINING_STATUS] == COMPLETED
                            or json_response[DATA][TRAINING_STATUS] == FAILED
                            or json_response[DATA][TRAINING_STATUS] == TIMED_OUT
                            or json_response[DATA][TRAINING_STATUS] == DEAD
                        ):
                            break
                    else:
                        console.print(
                            "> [red]ERROR[/red] Failed to fetch model details"
                        )
                        console.print(
                            f"> [red]ERROR[/red] Platform Response: \n {json.dumps(json_response, indent=4)}"
                        )
                        break
                    status.update(f"Model is {current_status} 🧍")
                    await sleep(wait_interval)
                    status.update(f"Model is {current_status} 🏋")
    return json_response


async def train_model(
    project_id: Text,
    language: Text,
    model_name: Text,
    wait: bool = True,
    wait_time: int = 1,
) -> Tuple[Dict[Text, Any], Dict[Text, Any]]:
    console.print(
        f"> [deep_sky_blue2]INFO[/deep_sky_blue2] Queuing training job for: "
        f"Project ID: {project_id}; Language: {language}; "
        f"[deep_sky_blue2]INFO[/deep_sky_blue2] Model Name: {model_name}"
    )
    payload = {PROJECT_ID: project_id, LANGUAGE: language, MODEL_NAME: model_name}
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()

    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{TRAIN_MODEL_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            console.print(
                "> [deep_sky_blue2]INFO[/deep_sky_blue2] Training job queued successfully"
            )
            model_id = json_response[DATA]["model_id"]
            last_model_status = await wait_till_training_completes(
                model_id, wait, wait_time
            )
        else:
            console.print("> [red]ERROR[/red] Failed to queue training job")
            console.print(f"> [red]ERROR[/red] {json_response['message']}")
            last_model_status = None
    return json_response, last_model_status


async def delete_models(model_id: Text) -> Dict[Text, Any]:
    console.print(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 🗑️ Deleting model with id: {model_id}")
    payload = {MODEL_ID: model_id}
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().delete(
        url=f"{neuralspace_url()}/{DELETE_MODELS_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            console.print("> [deep_sky_blue2]INFO[/deep_sky_blue2] ✅ Successfully deleted model")
        else:
            console.print("> [red]ERROR[/red] ❌ Failed to delete models")
            console.print(f"> Platform response: \n {json.dumps(json_response, indent=4)}")
    return json_response


async def deploy(model_id: Text, n_replicas: int) -> Dict[Text, Any]:
    logger.info(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] ⤴️ Deploying: Model ID: {model_id}; Replicas: {n_replicas};")
    payload = {MODEL_ID: model_id, N_REPLICAS: n_replicas}
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()

    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{DEPLOY_MODEL_URL}",
        data=json.dumps(payload),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            logger.info("> [deep_sky_blue2]INFO[/deep_sky_blue2] ✅ Model deployed successfully")
            logger.info(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] Platform Response: \n{json.dumps(json_response, indent=4)}")
        else:
            logger.error("> [red]ERROR[/red] ❌ Failed to deploy model")
            logger.error(f"> Platform response: \n{json.dumps(json_response, indent=4)}")
    return json_response


def print_nlu_response(nlu_response: Dict[Text, Any], response_time: float):
    table = Table(show_header=True, header_style="bold #c47900", show_lines=True)
    table.add_column("Text", style="#c47900")
    table.add_column("Intent", style="#c47900")
    table.add_column("Intent Confidence", style="#c47900")
    table.add_column("Response Time (sec)", style="#c47900")
    table.add_row(
            nlu_response[DATA]["text"][:30] + "[...]",
            nlu_response[DATA]["intent"]["name"],
            nlu_response[DATA]["intent"]["confidence"],
            str(response_time / 1000),
    )
    console.print(table)
    intent_ranking_table = Table(show_header=True, header_style="bold #c47900", show_lines=True)
    table.add_column("Intent", style="#c47900")
    table.add_column("Confidence", style="#c47900")

    for row in nlu_response[DATA]["intent_ranking"]:
        intent_ranking_table.add_row(
                row["name"],
                row["confidence"],
        )
    console.print(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] Intent Ranking")
    console.print(intent_ranking_table)
    formatted_entities = []
    for e in nlu_response["data"]["entities"]:
        e[START_INDEX] = e["start"]
        e[END_INDEX] = e["end"]
        formatted_entities.append(e)
    print_ner_response(formatted_entities, nlu_response["data"]["text"])


async def parse(model_id: Text, input_text: Text) -> Dict[Text, Any]:
    console.print(f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 📝 Parsing text: {input_text}, using Model ID: {model_id}")
    payload = {MODEL_ID: model_id, DATA: {TEXT: input_text}}
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()

    start = datetime.now()
    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{PARSE_URL}",
        data=json.dumps(payload, ensure_ascii=False),
        headers=HEADERS,
    ) as response:
        end = datetime.now()
        response_time = (end - start).microseconds
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            console.print("> [deep_sky_blue2]INFO[/deep_sky_blue2] ✅ Successfully parsed text")
            print_nlu_response(json_response, response_time)
        else:
            logger.error("> [red]ERROR[/red] ❌ Failed to parse model")
            logger.error(f"> Platform response: \n{json.dumps(json_response, indent=4)}")
    return json_response
