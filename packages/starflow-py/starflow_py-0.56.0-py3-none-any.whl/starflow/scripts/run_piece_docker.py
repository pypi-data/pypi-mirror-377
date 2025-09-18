from starflow.scripts.load_piece import load_piece_class_from_path, load_piece_models_from_path
from pathlib import Path
import os
import ast
import json


def run_piece():
     # Import Operator from File System, already configured with metadata
    piece_name = os.getenv("STARFLOW_PIECE")
    workspace_id = os.getenv("WORKSPACE_ID")

    pieces_repository_copy_path = Path("starflow/pieces_repository").resolve()
    pieces_folder_path = pieces_repository_copy_path / "pieces"
    compiled_metadata_path = pieces_repository_copy_path / ".starflow/compiled_metadata.json"

    with open(str(compiled_metadata_path), "r") as f:
        compiled_metadata = json.load(f)

    piece_class = load_piece_class_from_path(
        pieces_folder_path=pieces_folder_path,
        piece_name=piece_name,
        piece_metadata=compiled_metadata[piece_name]
    )

    piece_input_model_class, piece_output_model_class, piece_secrets_model_class = load_piece_models_from_path(
        pieces_folder_path=pieces_folder_path,
        piece_name=piece_name
    )

    # Instantiate Operator
    instantiate_op_dict = ast.literal_eval(os.getenv("STARFLOW_INSTANTIATE_PIECE_KWARGS"))
    piece_object = piece_class(**instantiate_op_dict)

    # Run Operator
    run_piece_input_kwargs = ast.literal_eval(os.getenv("STARFLOW_RUN_PIECE_KWARGS"))
    piece_object.run_piece_function(
        piece_input_data=run_piece_input_kwargs,        
        piece_input_model=piece_input_model_class, 
        piece_output_model=piece_output_model_class, 
        piece_secrets_model=piece_secrets_model_class,
        workspace_id=workspace_id
    )

    return None