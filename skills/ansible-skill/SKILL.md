---
name: ansible
description: "Infrastructure automation with Ansible. Use for server provisioning, configuration management, application deployment, and multi-host orchestration. Includes playbooks for OpenClaw VPS setup, security hardening, and common server configurations."
metadata: {"openclaw":{"requires":{"bins":["ansible","ansible-playbook"]},"install":[{"id":"ansible","kind":"pip","package":"ansible","bins":["ansible","ansible-playbook"],"label":"Install Ansible (pip)"}]}}

# Ansible Skill
Infrastructure as Code automation for server provisioning, configuration management, and orchestration.

## Quick Start

### Prerequisites
```bash

# Install Ansible
pip install ansible

# Or on macOS
brew install ansible

# Verify
ansible --version
```

# Test connection
ansible all -i inventory/hosts.yml -m ping

# Run playbook
ansible-playbook -i inventory/hosts.yml playbooks/site.yml

# Dry run (check mode)
ansible-playbook -i inventory/hosts.yml playbooks/site.yml --check

# With specific tags
ansible-playbook -i inventory/hosts.yml playbooks/site.yml --tags "security,nodejs"

## Directory Structure
skills/ansible/
├── SKILL.md # This file
├── inventory/ # Host inventories
│ ├── hosts.yml # Main inventory
│ └── group_vars/ # Group variables
├── playbooks/ # Runnable playbooks
│ ├── site.yml # Master playbook
│ ├── openclaw-vps.yml # OpenClaw VPS setup
│ └── security.yml # Security hardening
├── roles/ # Reusable roles
│ ├── common/ # Base system setup
│ ├── security/ # Hardening (SSH, fail2ban, UFW)
│ ├── nodejs/ # Node.js installation
│ └── openclaw/ # OpenClaw installation
└── references/ # Documentation
 ├── best-practices.md
 ├── modules-cheatsheet.md
 └── troubleshooting.md

## Core Concepts

### Inventory
Define your hosts in `inventory/hosts.yml`:

```yaml
all:
 children:
 vps:
 hosts:
 eva:
 ansible_host: 217.13.104.208
 ansible_user: root
 ansible_ssh_pass: "{{ vault_eva_password }}"
 plane:
 ansible_host: 217.13.104.99
 ansible_user: asdbot
 ansible_ssh_private_key_file: ~/.ssh/id_ed25519_plane

 openclaw:

### Playbooks
Entry points for automation:

# playbooks/site.yml - Master playbook
- name: Configure all servers
 hosts: all
 become: yes
 roles:
 - common
 - security

- name: Setup OpenClaw servers
 hosts: openclaw
 - nodejs
 - openclaw

### Roles
Reusable, modular configurations:

# roles/common/tasks/main.yml
- name: Update apt cache
 ansible.builtin.apt:
 update_cache: yes
 cache_valid_time: 3600
 when: ansible_os_family == "Debian"

- name: Install essential packages
 name:
 - curl, wget, git, htop, vim, unzip
 state: present

## Included Roles

### 1. common
Base system configuration:
- System updates, Essential packages, Timezone configuration
- User creation with SSH keys

### 2. security
Hardening following CIS benchmarks:
- SSH hardening (key-only, no root)
- fail2ban for brute-force protection
- UFW firewall configuration
- Automatic security updates

### 3. nodejs
Node.js installation via NodeSource:
- Configurable version (default: 22.x LTS)
- npm global packages
- pm2 process manager (optional)

### 4. openclaw
Complete OpenClaw setup:
- Node.js (via nodejs role)
- OpenClaw npm installation, Systemd service, Configuration file setup

# 1. Add host to inventory
cat >> inventory/hosts.yml << 'EOF'
 newserver:
 ansible_host: 1.2.3.4
 ansible_ssh_pass: "initial_password"
 deploy_user: asdbot
 deploy_ssh_pubkey: "ssh-ed25519 AAAA... asdbot"
EOF

# 2. Run OpenClaw playbook
ansible-playbook -i inventory/hosts.yml playbooks/openclaw-vps.yml \
 --limit newserver \
 --ask-vault-pass

# ansible_ssh_private_key_file: ~/.ssh/id_ed25519

### Pattern 2: Security Hardening Only
ansible-playbook -i inventory/hosts.yml playbooks/security.yml \
 --limit production \
 --tags "ssh,firewall"

# Update one server at a time
ansible-playbook -i inventory/hosts.yml playbooks/update.yml \
 --serial 1

# Check disk space on all servers
ansible all -i inventory/hosts.yml -m shell -a "df -h"

# Restart service
ansible openclaw -i inventory/hosts.yml -m systemd -a "name=openclaw state=restarted"

# Copy file
ansible all -i inventory/hosts.yml -m copy -a "src=./file.txt dest=/tmp/"

# inventory/group_vars/all.yml
timezone: Europe/Budapest
ssh_port: 22

# Security
security_ssh_password_auth: false
security_ssh_permit_root: false
security_fail2ban_enabled: true
security_ufw_enabled: true
security_ufw_allowed_ports:
 - 22, 80, 443

# Node.js
nodejs_version: "22.x"

# Create encrypted vars file
ansible-vault create inventory/group_vars/all/vault.yml

# Edit encrypted file
ansible-vault edit inventory/group_vars/all/vault.yml

# Run with vault
ansible-playbook site.yml --ask-vault-pass

# Or use vault password file
ansible-playbook site.yml --vault-password-file ~/.vault_pass

Vault file structure:

# inventory/group_vars/all/vault.yml
vault_eva_password: "y8UGHR1qH"
vault_deploy_ssh_key: |
 -----BEGIN OPENSSH PRIVATE KEY-----
 ...
 -----END OPENSSH PRIVATE KEY-----

## Common Modules
`apt`, Purpose=Package management (Debian), Example=`apt: name=nginx state=present`
`yum`, Purpose=Package management (RHEL), Example=`yum: name=nginx state=present`
`copy`, Purpose=Copy files, Example=`copy: src=file dest=/path/`
`template`, Purpose=Template files (Jinja2), Example=`template: src=nginx.conf.j2 dest=/etc/nginx/nginx.conf`
`file`, Purpose=File/directory management, Example=`file: path=/dir state=directory mode=0755`
`user`, Purpose=User management, Example=`user: name=asdbot groups=sudo shell=/bin/bash`
`authorized_key`, Purpose=SSH keys, Example=`authorized_key: user=asdbot key="{{ ssh_key }}"`
`systemd`, Purpose=Service management, Example=`systemd: name=nginx state=started enabled=yes`
`ufw`, Purpose=Firewall (Ubuntu), Example=`ufw: rule=allow port=22 proto=tcp`
`lineinfile`, Purpose=Edit single line, Example=`lineinfile: path=/etc/ssh/sshd_config regexp='^PermitRootLogin' line='PermitRootLogin no'`
`git`, Purpose=Clone repos, Example=`git: repo=https://github.com/x/y.git dest=/opt/y`
`npm`, Purpose=npm packages, Example=`npm: name=openclaw global=yes`
`command`, Purpose=Run command, Example=`command: /opt/script.sh`
`shell`, Purpose=Run shell command, Example=`shell: cat /etc/passwd \, grep root`

# Good
- name: Install nginx web server
 apt:
 name: nginx

# Bad
- apt: name=nginx

### 2. Use FQCN (Fully Qualified Collection Names)
- ansible.builtin.apt:

# Acceptable but less clear
- apt:

# Bad - implicit state

### 4. Idempotency
Write tasks that can run multiple times safely:

# Good - idempotent
- name: Ensure config line exists
 ansible.builtin.lineinfile:
 path: /etc/ssh/sshd_config
 regexp: '^PasswordAuthentication'
 line: 'PasswordAuthentication no'

# Bad - not idempotent
- name: Add config line
 ansible.builtin.shell: echo "PasswordAuthentication no" >> /etc/ssh/sshd_config

# tasks/main.yml
- name: Update SSH config
 ansible.builtin.template:
 src: sshd_config.j2
 dest: /etc/ssh/sshd_config
 notify: Restart SSH

# handlers/main.yml
- name: Restart SSH
 ansible.builtin.systemd:
 name: sshd
 state: restarted

### 6. Tags for Selective Runs
- name: Security tasks
 ansible.builtin.include_tasks: security.yml
 tags: [security, hardening]

- name: App deployment
 ansible.builtin.include_tasks: deploy.yml
 tags: [deploy, app]

# Test SSH connection manually
ssh -v user@host

# Debug Ansible connection
ansible host -i inventory -m ping -vvv

# Check inventory parsing
ansible-inventory -i inventory --list

### Common Errors
**"Permission denied"**
- Check SSH key permissions: `chmod 600 ~/.ssh/id_*`
- Verify user has sudo access
- Add `become: yes` to playbook

**"Host key verification failed"**
- Add to ansible.cfg: `host_key_checking = False`
- Or add host key: `ssh-keyscan -H host >> ~/.ssh/known_hosts`

**"Module not found"**
- Use FQCN: `ansible.builtin.apt` instead of `apt`
- Install collection: `ansible-galaxy collection install community.general`

# Verbose output
ansible-playbook site.yml -v # Basic
ansible-playbook site.yml -vv # More
ansible-playbook site.yml -vvv # Maximum

# Step through tasks
ansible-playbook site.yml --step

# Start at specific task
ansible-playbook site.yml --start-at-task="Install nginx"

# Check mode (dry run)
ansible-playbook site.yml --check --diff

# Run playbook via exec tool
exec command="ansible-playbook -i skills/ansible/inventory/hosts.yml skills/ansible/playbooks/openclaw-vps.yml --limit eva"

# Ad-hoc command
exec command="ansible eva -i skills/ansible/inventory/hosts.yml -m shell -a 'systemctl status openclaw'"

### Storing Credentials
Use OpenClaw's Vaultwarden integration:

# Get password from vault cache
PASSWORD=$(.secrets/get-secret.sh "VPS - Eva")

# Use in ansible (not recommended - use ansible-vault instead)
ansible-playbook site.yml -e "ansible_ssh_pass=$PASSWORD"

Better: Store in Ansible Vault and use `--ask-vault-pass`.

## References
- `references/best-practices.md` - Detailed best practices guide
- `references/modules-cheatsheet.md` - Common modules quick reference
- `references/troubleshooting.md` - Extended troubleshooting guide

## External Resources
- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/) - Community roles
- [geerlingguy roles](https://github.com/geerlingguy?tab=repositories&q=ansible-role) - High quality roles
- [Ansible for DevOps](https://www.ansiblefordevops.com/) - Book by Jeff Geerling