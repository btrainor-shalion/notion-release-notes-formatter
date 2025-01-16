import os
import sys
import shutil
import uuid
from urllib.parse import unquote
from bs4 import BeautifulSoup

# Global S3 bucket base URL
s3_bucket_base_url = "https://d3cf387e7yjscm.cloudfront.net"

def get_filename_from_cli_or_prompt():
    """
    Get the filename from the command line or prompt the user if not provided.
    """
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"Filename provided via CLI: {filename}")
        return filename
    filename = input("Enter the filename (with or without .html extension): ").strip()
    print(f"Filename provided via input: {filename}")
    return filename

def ensure_html_extension(filename):
    """
    Ensure the filename has an .html extension.
    """
    if not filename.endswith('.html'):
        filename += '.html'
        print(f"Ensured HTML extension: {filename}")
    return filename

def get_base_directory(filename):
    """
    Determine the base directory of the file.
    """
    if os.path.isabs(filename):
        base_directory = os.path.dirname(filename)
    else:
        base_directory = os.getcwd()
    print(f"Base directory determined: {base_directory}")
    return base_directory

def restructure_body_add_header_footer_and_wrap(html_file):
    """
    Replace <body> with <main>, add a header and footer, and wrap content in a styled div.
    """
    print("\n--- Restructuring <body> ---")
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    body = soup.body
    if not body:
        print("No <body> element found. Exiting restructuring.")
        return soup

    # Rename body to <main>
    main = soup.new_tag("main")
    main.extend(body.contents)  # Move all body contents into <main>

    # Header HTML
    header = BeautifulSoup("""
    <header style="margin-bottom: 60px; text-align: center">

      <p style="color: lightgrey; font-family: sans-serif; font-weight: bold">THE TECH TEAM</p>
    <br>

      <!-- The logo image has been uploaded into our private S3 bucket used for release note images -->
    <img src="{}/shalion-logo-light@2x.png" width="188px" height="40px">

    <h1 class="page-title" style="text-align: center">🥳 We've updated the Console!</h1>
    <p>Check out the release notes below to see what's new, improved, and fixed.</p>

  </header>
    """.format(s3_bucket_base_url), 'html.parser')

    # Footer HTML
    footer = BeautifulSoup("""
    <footer style="text-align: center">

  <hr style="background-color: #f2f2f2; border-radius: 16px; display: block; height: 2px; margin: 0 auto; margin-top: 32px; margin-bottom: 64px; width: 100px; text-align: center;">
  <p>As always, if you have any questions or concerns regarding these changes please let us know by responding to this email or through the usual channels.</p>
  <br>
  <br>
  <p><strong>THE TECH TEAM</strong></p>
  <br>
  <!-- The logo image has been uploaded into our private S3 bucket used for release note images -->
  <img src="{}/shalion-logo-light@2x.png" width="113px" height="24px">
  <br>
  <br>

<p>This message and its attachments are intended solely for the recipient and may contain confidential information subject to professional secrecy. Reproduction or distribution without express authorization is prohibited. If you are not the intended recipient, please delete it and inform us through this channel. In accordance with current data protection regulations, we inform you that your personal data and email address are part of a file, the responsibility of Shalion Data Services S.L. The purpose of the file is to maintain, develop, and monitor the contractual and business relationship, as well as to send you information about products and services of our own or related to your sector of activity. If you wish, you may exercise your rights of access, rectification, cancellation, and opposition by email to: privacy@shalion.com, indicating the right you wish to exercise in the subject line.</p>

</footer>
    """.format(s3_bucket_base_url), 'html.parser')

    # Wrapper <div>
    wrapper_div = soup.new_tag("div", style="width: 640px; margin: 0 auto; padding: 20px;")
    wrapper_div.append(header)
    wrapper_div.append(main)
    wrapper_div.append(footer)

    # Replace <body> with the wrapper div
    body.replace_with(wrapper_div)

    print("Body successfully replaced with <main> and wrapped with a styled <div>.")
    return soup


def process_images_and_update_src(soup, base_directory):
    """
    Process images: rename files, move them, and update <img> tags.
    """

    renamed_files = {}

    print("\n--- Starting Image Processing ---")
    for tag in soup.find_all("img", src=True):
        original_src = tag['src']

        # Skip external URLs
        if original_src.startswith('http://') or original_src.startswith('https://'):
            print(f"External image found, skipping: {original_src}")
            continue

        # Decode the URL-encoded file path
        decoded_src = unquote(original_src)

        # Resolve the full original path
        src_directory, src_filename = os.path.split(decoded_src)
        original_image_path = os.path.join(base_directory, decoded_src)  # Use decoded path

        # Check if this file was already renamed
        if original_image_path in renamed_files:
            new_image_name = renamed_files[original_image_path]
            print(f"Using cached renamed file for: {original_image_path}")
        else:
            # Generate a new UUID-based filename
            new_image_uuid = str(uuid.uuid4())
            file_ext = os.path.splitext(src_filename)[1]
            new_image_name = f"{new_image_uuid}{file_ext}"

            # Build the new image path in the same folder as the original image
            new_image_directory = os.path.join(base_directory, src_directory)
            os.makedirs(new_image_directory, exist_ok=True)  # Ensure the directory exists
            new_image_path = os.path.join(new_image_directory, new_image_name)

            # Move the image to the new path
            shutil.move(original_image_path, new_image_path)
            print(f"Renamed and moved: '{original_image_path}' -> '{new_image_path}'")

            # Cache the renamed file
            renamed_files[original_image_path] = new_image_name

        # Update the <img> tag src attribute
        new_src = f"{s3_bucket_base_url}/{new_image_name}"
        tag["src"] = new_src
        print(f"Updated image src: {new_src}")

        # Update parent <a> tag href (if any)
        parent_a_tag = tag.find_parent('a')
        if parent_a_tag and 'href' in parent_a_tag.attrs:
            parent_a_tag['href'] = new_src
            print(f"Updated parent <a> href: {new_src}")

    print("--- Image Processing Complete ---\n")


def set_image_width_inside_main(soup):
    """
    Update all images inside the <main> tag to have width: 100%.
    """
    print("\n--- Updating Image Widths in <main> ---")
    main_element = soup.find('main')
    if not main_element:
        print("No <main> element found. Skipping image width updates.")
        return

    for img in main_element.find_all('img'):
        img['style'] = 'width: 100%'
        print(f"Updated <img> tag to width 100%: {img}")
    print("--- Image Width Updates Complete ---\n")

def save_html_to_file(soup, html_file):
    """
    Save the modified HTML content back to the file.
    """
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
    print(f"HTML file successfully saved: {html_file}")

def main():
    """
    Main function to coordinate all operations.
    """
    filename = get_filename_from_cli_or_prompt()
    if not filename:
        print("No filename provided. Exiting.")
        sys.exit(1)

    filename = ensure_html_extension(filename)
    base_directory = get_base_directory(filename)

    # Step 1: Restructure body and add header/footer
    with open(filename, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    soup = restructure_body_add_header_footer_and_wrap(filename)

    # Step 2: Process images (rename and update src)
    process_images_and_update_src(soup, base_directory)

    # Step 3: Update image widths inside <main>
    set_image_width_inside_main(soup)

    # Step 4: Save the updated HTML
    save_html_to_file(soup, filename)

if __name__ == "__main__":
    main()
