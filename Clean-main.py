import os
import shutil
import tempfile
from win11toast import toast

from icons_utils import update_icon


def get_dir_stats(path):
    count, size = 0, 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                size += os.path.getsize(fp)
                count += 1
            except OSError:
                pass
    return count, size


def main():
    temp_dir = tempfile.gettempdir()
    deleted_files, deleted_dirs, skipped = 0, 0, 0
    total_size = 0

    for entry in os.listdir(temp_dir):
        full_path = os.path.join(temp_dir, entry)
        try:
            if os.path.isfile(full_path) or os.path.islink(full_path):
                file_size =  os.path.getsize(full_path)
                os.remove(full_path)
                total_size += file_size
                deleted_files += 1
            elif os.path.isdir(full_path):
                files_inside, size_inside = get_dir_stats(full_path)
                shutil.rmtree(full_path)
                deleted_files += files_inside
                total_size += size_inside
                deleted_dirs += 1
        except (PermissionError, OSError):
            skipped += 1

    total_mb = total_size / (1024 * 1024)

    toast(
        "Memory Defender",
        f"Deleted folders and filed: {deleted_files+deleted_dirs}\nFresh space: {total_mb:.2f} МБ",
        app_id="Memory Defender"
    )
    update_icon()


if __name__ == '__main__':
    main()