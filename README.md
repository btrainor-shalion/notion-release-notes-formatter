# Notion release notes formatter

This script formats an **HTML file exported from Notion** to make it suitable for email distribution. It performs the following tasks:

- ✅ Adds a header and footer for consistent formatting and branding.
- ✅ Renames image URLs to allow direct insertion into an email body.

⚠️ **Important Manual Step**

For images to display correctly, all renamed images **must be uploaded** to the `prod-shalion-release-notes` S3 bucket.

The renamed URLs use an internally generated AWS S3 domain, ensuring seamless reference to the images without requiring manual adjustments in the email content.
