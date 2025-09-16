from huggingface_hub import HfApi

dummy_repo_id = "georgiosrizos/spider-monkey-dummy-detector"
local_dir = "C:\\Users\\George\\scp_folder\\exported_graphs"

api = HfApi()
api.upload_folder(
    folder_path=local_dir,
    repo_id=dummy_repo_id,
    repo_type="model"
)
