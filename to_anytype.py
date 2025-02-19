"""
This script converts your Wiki-links and both type of Markdown links (relative and not relative) to one format of Markdown links: Markdown links with relative path.
This output format suit for AnyType.
Part1: bringing existing Markdown links to one format for future processing
Part2: changing [[wiki-links]] to [markdown-links](markdown-links.md)
Part3: creating relative path for all links and creating new if they do not exist. And creating Folders links (Folders links contain links to all included files)
Part4: just changing " " to "%20" for Markdown standard
Part5: remove dashes from metatags. Metatags to text.
"""

import os
import re
import datetime
from pathlib import Path

# Update base path to use Windows path format
base_path = r'your\obsidian\vault'
newfiles_folder = 'newnoteflow'

# Initialize log file with better formatting
log = open("log.txt", "w", encoding='utf-8')
log.write("# Anytype Migration Script Log\n\n")
log.write(f"## Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
log.write(f"Base path: `{base_path}`\n\n")

def log_section(name):
    """Add a section header to the log"""
    log.write(f"\n## {name}\n")

def log_subsection(name):
    """Add a subsection header to the log"""
    log.write(f"\n### {name}\n")

def log_file(filepath):
    """Log file processing with proper indentation"""
    log.write(f"- Processing: `{Path(filepath).name}`\n")

def log_change(original, updated):
    """Log link changes with proper indentation"""
    log.write(f"  - Changed: `{original}` → `{updated}`\n")

def log_error(message):
    """Log errors with proper highlighting"""
    log.write(f"⚠️ **ERROR**: {message}\n")

def log_success(message):
    """Log success messages"""
    log.write(f"✅ {message}\n")

# Part1
def preprocess_md_links(file_path):
    """Preprocess Markdown links: replace %20 with spaces and change relative paths to absolute."""
    try:
        log_file(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()

        # Replace %20 with spaces
        contents = re.sub(r'%20', ' ', contents)
        
        def remove_relative_path(match):
            name, path = match.groups()
            if path.startswith(("http:", "https:", "onenote:")):
                log_change(f"[{name}]({path})", f"[{name}]({path})")
                return f"[{name}]({path})"
            filename = os.path.basename(path)
            log_change(f"[{name}]({path})", f"[{name}]({filename})")
            return f"[{name}]({filename})"

        contents = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', remove_relative_path, contents)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(contents)
        log_success(f"Processed {Path(file_path).name}")
    except Exception as e:
        log_error(f"Failed to preprocess {Path(file_path).name}: {str(e)}")

# Part2
def replace_wiki_links(file_path):
    try:
        log_file(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()

        def replace_function(match):
            link_content = match.group(1)
            if link_content.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.md')):
                log_change(f"[[{link_content}]]", f"[{link_content}]({link_content})")
                return f"[{link_content}]({link_content})"
            else:
                log_change(f"[[{link_content}]]", f"[{link_content}]({link_content}.md)")
                return f"[{link_content}]({link_content}.md)"

        pattern = r'\[\[(.*?)\]\]'
        contents = re.sub(pattern, replace_function, contents)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(contents)
        log_success(f"Processed wiki links in {Path(file_path).name}")
    except Exception as e:
        log_error(f"Failed to process wiki links in {Path(file_path).name}: {str(e)}")

# Part3
def find_file(name, search_path):
    for root, dirs, files in os.walk(search_path):
        if name in files:
            return os.path.join(root, name)
    return None

def create_if_not_exists(file_path):
    try:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('')
            log_success(f"Created new file: {Path(file_path).name}")
        else:
            log.write(f"- File exists: `{Path(file_path).name}`\n")
    except Exception as e:
        log_error(f"Failed to create {Path(file_path).name}: {str(e)}")

def update_links_and_create_directory_index(file_path, base_path):
    try:
        log_file(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()

        def replace_link(match):
            is_image, name, link = match.groups()
            if link.startswith(("http:", "https:", "onenote:")):
                log.write(f"  - External link: `{link}`\n")
                return match.group(0)
            
            found_path = find_file(link, base_path)
            if found_path:
                relative_path = os.path.relpath(found_path, start=os.path.dirname(file_path))
                log_change(f"{is_image}[{name}]({link})", f"{is_image}[{name}]({relative_path})")
            else:
                if is_image == '':
                    newfiles_path = os.path.join(base_path, newfiles_folder, link)
                    create_if_not_exists(newfiles_path)
                    relative_path = os.path.relpath(newfiles_path, start=os.path.dirname(file_path))
                else:
                    log.write(f"  - Keeping image link: `{link}`\n")
                    relative_path = link
            return f"{is_image}[{name}]({relative_path})"

        pattern = r'(!?)\[([^\]]+)\]\(([^)]+)\)'
        contents = re.sub(pattern, replace_link, contents)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(contents)
        log_success(f"Updated links in {Path(file_path).name}")
    except Exception as e:
        log_error(f"Failed to update links in {Path(file_path).name}: {str(e)}")

def create_directory_index(dir_path):
    try:
        index_file_path = os.path.join(dir_path, os.path.basename(dir_path) + '.md')
        if not os.path.exists(index_file_path):
            links = []
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    links.append(f"- [{item}]({os.path.abspath(os.path.join(item_path, item + '.md'))})")
                elif item.endswith('.md') and item != os.path.basename(dir_path) + '.md':
                    links.append(f"- [{os.path.splitext(item)[0]}]({os.path.abspath(item_path)})")
            with open(index_file_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(links))
            log_success(f"Created index for {Path(dir_path).name}")
        else:
            log.write(f"- Index exists: `{Path(dir_path).name}`\n")
    except Exception as e:
        log_error(f"Failed to create index for {Path(dir_path).name}: {str(e)}")

# Part4
def update_md_links(file_path):
    try:
        log_file(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        contents = re.sub(pattern, lambda m: f'[{m.group(1)}]({m.group(2).replace(" ", "%20")})', contents)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(contents)
        log_success(f"Updated spaces in {Path(file_path).name}")
    except Exception as e:
        log_error(f"Failed to update spaces in {Path(file_path).name}: {str(e)}")

# Part5
def metategs_to_text(file_path):
    try:
        log_file(file_path)
        with open(file_path, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            modified_lines = [line for i, line in enumerate(lines) if i >= 9 or (line.strip() != '---')]
            f.seek(0)
            f.writelines(modified_lines)
            f.truncate()
        log_success(f"Removed metatags from {Path(file_path).name}")
    except Exception as e:
        log_error(f"Failed to remove metatags from {Path(file_path).name}: {str(e)}")

### Main Execution
log_section("Migration Process")
log.write(f"🕒 Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

stats = {
    'files_processed': 0,
    'wiki_links_converted': 0,
    'directories_indexed': 0,
    'errors': 0
}

# Execute all parts
parts = [
    ("Preprocessing Markdown Links", preprocess_md_links),
    ("Converting Wiki Links", replace_wiki_links),
    ("Updating Link Paths", update_links_and_create_directory_index),
    ("Encoding Spaces", update_md_links),
    ("Removing Metatags", metategs_to_text)
]

for part_num, (part_name, part_func) in enumerate(parts, 1):
    print(f"\nPart {part_num}: {part_name}")
    execute = input(f"Do you want to execute {part_name}? (y/n): ").lower()
    
    if execute != 'y':
        print(f"Skipping {part_name}")
        log.write(f"\n⏭️ Skipped Part {part_num}: {part_name}\n")
        continue
    
    log_section(f"Part {part_num}: {part_name}")
    files_in_part = 0
    
    for root, dirs, files in os.walk(base_path):
        current_dir = Path(root).name
        log_subsection(f"📁 Processing Directory: {current_dir}")
        
        if part_func == update_links_and_create_directory_index:
            for dir in dirs:
                log.write(f"📂 Indexing directory: `{dir}`\n")
                create_directory_index(os.path.join(root, dir))
                stats['directories_indexed'] += 1
        
        md_files = [f for f in files if f.endswith('.md')]
        if md_files:
            log.write(f"📄 Found {len(md_files)} Markdown files\n")
            for file in md_files:
                filepath = os.path.join(root, file)
                if part_func == update_links_and_create_directory_index:
                    part_func(filepath, base_path)
                else:
                    part_func(filepath)
                files_in_part += 1
                stats['files_processed'] += 1
    
    log.write(f"\n✅ Completed Part {part_num}: {files_in_part} files processed\n")

log_section("📊 Summary")
log.write("### Statistics\n")
log.write(f"- 📄 Total files processed: {stats['files_processed']}\n")
log.write(f"- 📂 Directories indexed: {stats['directories_indexed']}\n")
log.write(f"- ⚠️ Errors encountered: {stats['errors']}\n")
log.write(f"\n🏁 Completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

log.close()
print("✨ Migration completed. Check log.txt for details.")
