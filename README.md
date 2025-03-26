# Notion release notes formatter

A Python script to format Notion HTML exports for email-friendly release notes.

This script basically takes an HTML file exported from Notion, adds a header and footer and renames image URLs.

This script processes an HTML file exported from Notion by:

1. **Adding a header and footer** for consistency and branding.
2. **Renaming image URLs** to facilitate direct insertion into an email body.

⚠️ **Important Manual Step**

For images to display correctly, all renamed images **must be uploaded** to the `prod-shalion-release-notes` S3 bucket.

The renamed URLs use an internally generated AWS S3 domain, ensuring seamless reference to the images without requiring manual adjustments in the email content.
