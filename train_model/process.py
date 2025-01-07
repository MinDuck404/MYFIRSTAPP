import os
import shutil

def split_dataset(src_dir, dest_train_dir, dest_test_dir):
    """
    Split dataset into train and test based on subfolders.

    Args:
        src_dir (str): Path to the source dataset.
        dest_train_dir (str): Path to the training dataset folder.
        dest_test_dir (str): Path to the testing dataset folder.
    """
    for pokemon_name in os.listdir(src_dir):
        pokemon_path = os.path.join(src_dir, pokemon_name)
        if not os.path.isdir(pokemon_path):
            continue

        # Duyệt qua thư mục 'all'
        all_path = os.path.join(pokemon_path, 'all')
        if os.path.exists(all_path):
            # Duyệt qua base và mega
            for variant in os.listdir(all_path):
                variant_path = os.path.join(all_path, variant)
                if not os.path.isdir(variant_path):
                    continue

                # Lấy danh sách các form (christmas, none, shiny,...)
                forms = [d for d in os.listdir(variant_path) if os.path.isdir(os.path.join(variant_path, d))]
                print(f"\nPokemon: {pokemon_name}, Variant: {variant}")
                print(f"Forms: {forms}")

                if forms:
                    # Form đầu tiên vào test
                    test_form = forms[0]
                    print(f"Test form selected: {test_form}")

                    # Copy files cho mỗi form
                    for form in forms:
                        form_path = os.path.join(variant_path, form)
                        relative_path = os.path.relpath(form_path, src_dir)

                        # Quyết định đường dẫn đích
                        if form == test_form:
                            dest_folder = os.path.join(dest_test_dir, relative_path)
                            print(f"-> Moving to test: {relative_path}")
                        else:
                            dest_folder = os.path.join(dest_train_dir, relative_path)
                            print(f"-> Moving to train: {relative_path}")

                        # Tạo thư mục đích và copy files
                        os.makedirs(dest_folder, exist_ok=True)
                        for file in os.listdir(form_path):
                            if file.endswith(".png"):
                                src_file = os.path.join(form_path, file)
                                dest_file = os.path.join(dest_folder, file)
                                shutil.copy(src_file, dest_file)
                                print(f"Copied {src_file} to {dest_file}")

    print(f"\nDataset has been split into train ({dest_train_dir}) and test ({dest_test_dir}).")

# Đường dẫn dữ liệu nguồn và đích
src_directory = r"train"  # Đường dẫn dataset gốc
train_directory = r"output_train"  # Đường dẫn thư mục train
test_directory = r"output_test"  # Đường dẫn thư mục test

# Thực thi phân chia dữ liệu
split_dataset(src_directory, train_directory, test_directory)