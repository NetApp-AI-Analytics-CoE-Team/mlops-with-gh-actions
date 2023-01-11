from kfp.components import InputPath,OutputPath

def markdown_vis(
    input_history_path:InputPath('history'),
    mlpipeline_ui_metadata_path: OutputPath(),
    mlpipeline_metrics_path: OutputPath('Metrics')
    ):
    import json
    import pandas

    # open output file from train step
    with open(input_history_path, mode='r') as f:
        data = json.loads(f.read())

    # convert history json to markdown
    df = pandas.DataFrame.from_dict(data)
    df.insert(0, 'epochs', range(1, len(df.index) + 1))
    df_md = df.to_markdown(index=False, tablefmt="grid")
        
    metadata = {
        'outputs' : [
        # Markdown that is hardcoded inline
        {
            'storage': 'inline',
            'source': f'# Training Result\n{df_md}\n',
            'type': 'markdown',
        },
        ]
    }

    # write markdown visualizer
    with open(mlpipeline_ui_metadata_path, 'w') as metadata_file:
        json.dump(metadata, metadata_file)

    # get last epoch's metrics
    accuracy = df.tail(1).iloc[0]["accuracy"]
    val_accuracy = df.tail(1).iloc[0]["val_accuracy"]

    # create metrics
    metrics = {
        'metrics': [
            {
            'name': 'accuracy-score', # The name of the metric. Visualized as the column name in the runs table.
            'numberValue':  accuracy, # The value of the metric. Must be a numeric value.
            'format': "PERCENTAGE",   # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
            },
            {
            'name': 'validation-accuracy-score', # The name of the metric. Visualized as the column name in the runs table.
            'numberValue':  val_accuracy, # The value of the metric. Must be a numeric value.
            'format': "PERCENTAGE",   # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
            },
        ]
    }

    # write metrics data
    with open(mlpipeline_metrics_path, 'w') as f:
        json.dump(metrics, f)