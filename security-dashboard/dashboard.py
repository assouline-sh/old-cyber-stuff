from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
#from rich.text import Text
#import re
import subprocess
import typer

app = typer.Typer()
console = Console()


# Helper function to run shell commands
def run_cmd(cmd):
	try:
    	result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    	if result.returncode == 0:
        	return result.stdout.strip()
    	else:
        	return result.stderr.strip()
	except Exception as e:
    	return str(e)


# First dashboard, showing primarily system information
def system_dashboard():
	console.print("====================================================================[bold green]System_Dashboard[/bold green]===================================================================")
    
	# Execute commands
	hostname = run_cmd("hostnamectl")
	package_support = run_cmd("sudo check-support-status | grep 'Source:' | awk -F 'Source:' '{print $2}' | tr -d ' '")
	users = run_cmd("getent passwd | awk -F: '$7 ~ /(\/bin\/bash|\/bin\/sh)/ {print $1}'")
	sudo_users = run_cmd("grep -Po '^sudo.+:\K.*$' /etc/group")
	groups = run_cmd("getent group | awk -F: '$3 >= 1000 {print $1}'")
	login = run_cmd("last | awk '!/reboot/ {print $1, $2, $3, $4, $5, $6, $7, $8, $9, $10}'")
	clamav = run_cmd("clamscan -i -r")
	rkhunter = run_cmd("sudo rkhunter --check -q --sk --propupd; sudo grep -E 'Warning:' /var/log/rkhunter.log")

	# Combine several command outputs for placement in a single panel
	sysinfo_output = f"[bold]System Info[/bold]:\n{hostname}\n\n[bold]Limited Security Support for Packages[/bold]:\n{package_support}"
	users_output = f"[bold]Users[/bold]:\n{users}\n\n[bold]Sudo Users:[/bold]\n{sudo_users}"
    
	# Create panels
	sysinfo_panel = Panel(sysinfo_output, title="System Info", border_style="blue")
	users_panel = Panel(users_output, title="Users", border_style="blue")
	groups_panel = Panel(groups, title="Groups", border_style="blue")
	login_panel = Panel(login, title="Last Logins", border_style="blue")
	clamav_panel = Panel(clamav, title="ClamAV", border_style="blue")
	rkhunter_panel = Panel(rkhunter, title="Rkhunter", border_style="blue", height=10)

	# Place panels in the layout
	layout = Layout()
	layout.split_column(
    	Layout(name="upper"),
    	Layout(name="middle"),
    	Layout(rkhunter_panel, name="bottom")
	)
	layout["upper"].split_row(
    	Layout(sysinfo_panel, name="upper_left"),
    	Layout(name="upper_right")
	)
	layout["upper_right"].split_row(
    	Layout(users_panel, name="upper_right_left"),
    	Layout(groups_panel, name="upper_right_right")
	)
	layout["middle"].split_row(
    	Layout(login_panel, name="middle_left"),
    	Layout(clamav_panel, name="middle_right")
	)

	# Render the dashboard
	console.print(layout)

	input("Press enter to continue to Network Dashboard...")
    

# Second dashboard, showing primarily network information
def network_dashboard():
	console.print("=================================================================[bold green]Network_Dashboard[/bold green]================================================================")
	# Execute commands
	ipaddr = run_cmd("ip -4 -o addr show | awk '{print $1, $2, $3, $4}'")
	iproute = run_cmd("ip route show | awk -F 'src' '{print $1}'")
	iprule = run_cmd('ip rule show')
	ufw = run_cmd('sudo ufw status &>/dev/null && sudo ufw status verbose')
	netstat = run_cmd('netstat -tulpna')
	ps = run_cmd('ps aux --sort=-%cpu | head')

	# Combine several command outputs for placement in a single panel
	ipinfo_output = f"[bold]IP Address:[/bold]\n{ipaddr}\n\n[bold]IP Route:[/bold]\n{iproute}\n\n[bold]IP Rule:[/bold]\n{iprule}"
    
	# Create panels
	ipinfo_panel = Panel(ipinfo_output, title="IP Info", border_style="blue")
	ufw_panel = Panel(ufw, title="UFW Rules", border_style="blue")
	netstat_panel = Panel(netstat, title="Network Connections", border_style="blue")
	ps_panel = Panel(ps, title="Processes", border_style="blue")

	# Place panels in the layout
	layout = Layout()
	layout.split_column(
    	Layout(name="upper"),
    	Layout(netstat_panel, name="middle"),
    	Layout(ps_panel, name="bottom")
	)
	layout["upper"].split_row(
    	Layout(ipinfo_panel, name="upper_left"),
    	Layout(ufw_panel, name="upper_right")
	)

	# Render the dashboard
	console.print(layout)


@app.command()
# Render dashboards
def render_dashboards():
	system_dashboard()
	network_dashboard()

if __name__ == "__main__":
	app()

