from kfp.components import InputPath,OutputPath

def markdown_vis(
    input_history_path:InputPath('history'),
    mlpipeline_ui_metadata_path: kfp.components.OutputPath()
    ):
    import json
    import pandas

    # open output file from train step
    with open(input_history_path, mode='r') as f:
        data = json.loads(f.read())

    # convert history json to markdown
    df = pandas.DataFrame.from_dict(data)
    df_md = df.to_markdown(index=False)
        
    metadata = {
        'outputs' : [
        # Markdown that is hardcoded inline
        {
            'storage': 'inline',
            'source': f'# Training Result\n{df_md}',
            'type': 'markdown',
        },
        ]
    }

    with open(mlpipeline_ui_metadata_path, 'w') as metadata_file:
        json.dump(metadata, metadata_file)