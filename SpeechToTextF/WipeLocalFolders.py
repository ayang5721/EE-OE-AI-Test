import os

# Wipe the local_transcripts folder
def wipe_local_folders(output_folder):
    if os.path.exists(output_folder):
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    else:
        print(f"Output folder '{output_folder}' does not exist.")


wipe_local_folders("local_transcripts")