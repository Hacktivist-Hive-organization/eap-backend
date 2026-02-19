




Working with Visual Studio Code

Install extensions:
- nginx.conf
- Remote - SSH

cmd + shift + . to show hidden files and folders.


Then:

Open VS Code

Press Ctrl + Shift + P

Run:

Remote-SSH: Connect to Host


Add your VPS:

ssh user@your-server-ip


Then VS Code opens the remote machine like a local workspace.

You get:

✅ File explorer
✅ Syntax highlighting
✅ Search
✅ Terminal
✅ Copy/paste files
✅ No nano needed

You can browse:

/etc/nginx/


and:

/var/www/


like normal folders.

To open a file or folder with the terminal, use:
code -r /path/to/your/file/or/folder

VS Code doesn’t always recognize nginx config files automatically — especially when they don’t have a .conf extension, like:

/etc/nginx/sites-enabled/eap-it31.motoppdemo.nl


VS Code just treats it as plain text.

✅ Fix for the current file (one-time)

At the bottom-right corner of VS Code:

Click where it says Plain Text
![img_3.png](img_3.png)

Type:

nginx


Select nginx

Syntax highlighting should appear immediately.

✅ Permanent fix (recommended)

Tell VS Code to treat nginx config paths as nginx files.

Open VS Code settings JSON:

Ctrl+Shift+P → Preferences: Open Settings (JSON)


Add:

"files.associations": {
    "/etc/nginx/sites-available/*": "nginx",
    "/etc/nginx/sites-enabled/*": "nginx",
    "*.conf": "nginx"
}
(The permanent fix did not work for me)

Now nginx configs will always open with highlighting.

![img_2.png](img_2.png)

![img_1.png](img_1.png)
