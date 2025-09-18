import os
from cogwit_sdk import cogwit, CogwitConfig, SearchType
from cogwit_sdk.responses import AddResponse, CognifyResponse, CombinedSearchResult

cogwit_config = CogwitConfig(
    api_key=os.getenv("COGWIT_API_KEY", ""),
)

cogwit_instance = cogwit(cogwit_config)


async def main():
    result = await cogwit_instance.add(
        data="Test data",
        dataset_name="test_dataset",
    )

    assert isinstance(result, AddResponse)
    assert result.status == "PipelineRunCompleted"
    assert "test_dataset" == result.dataset_name

    dataset_id = result.dataset_id

    result = await cogwit_instance.cognify(
        dataset_ids=[dataset_id],
    )
    print(result)
    assert isinstance(result, CognifyResponse)
    dataset_result = result[str(dataset_id)]
    assert dataset_result.status == "PipelineRunCompleted"
    assert dataset_result.dataset_name == "test_dataset"

    search_results = await cogwit_instance.search(
        query_text="What is in data?",
        query_type=SearchType.GRAPH_COMPLETION,
        use_combined_context=True,
    )

    assert isinstance(search_results, CombinedSearchResult)
    assert search_results.datasets[0].id == dataset_id


import asyncio

asyncio.run(main())
