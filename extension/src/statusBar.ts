import * as vscode from 'vscode';

export enum ServerStatus {
    Idle = 'idle',
    Processing = 'processing',
    Error = 'error',
    Disconnected = 'disconnected'
}

export class HeliosStatusBar {
    private statusBarItem: vscode.StatusBarItem;
    private currentStatus: ServerStatus = ServerStatus.Disconnected;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.command = 'helios.statusBarClick';
        this.statusBarItem.show();
        this.updateStatusBar();

        // Register status bar click command
        vscode.commands.registerCommand('helios.statusBarClick', () => {
            this.showStatusMenu();
        });
    }

    setStatus(status: ServerStatus): void {
        this.currentStatus = status;
        this.updateStatusBar();
    }

    private updateStatusBar(): void {
        switch (this.currentStatus) {
            case ServerStatus.Idle:
                this.statusBarItem.text = '$(robot) Helios';
                this.statusBarItem.backgroundColor = undefined;
                this.statusBarItem.tooltip = 'Helios is ready for code completion';
                break;
            case ServerStatus.Processing:
                this.statusBarItem.text = '$(loading~spin) Helios';
                this.statusBarItem.backgroundColor = undefined;
                this.statusBarItem.tooltip = 'Helios is generating completion...';
                break;
            case ServerStatus.Error:
                this.statusBarItem.text = '$(error) Helios';
                this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
                this.statusBarItem.tooltip = 'Helios encountered an error';
                break;
            case ServerStatus.Disconnected:
                this.statusBarItem.text = '$(debug-disconnect) Helios';
                this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
                this.statusBarItem.tooltip = 'Helios server is disconnected';
                break;
        }
    }

    private async showStatusMenu(): Promise<void> {
        const config = vscode.workspace.getConfiguration('helios');
        const enabled = config.get<boolean>('enabled', true);
        
        const items: vscode.QuickPickItem[] = [
            {
                label: enabled ? '$(circle-large-filled) Disable Helios' : '$(circle-large-outline) Enable Helios',
                description: enabled ? 'Turn off code completion' : 'Turn on code completion'
            },
            {
                label: '$(refresh) Restart Server',
                description: 'Restart the local inference server'
            },
            {
                label: '$(gear) Open Settings',
                description: 'Configure Helios settings'
            },
            {
                label: '$(info) Server Status',
                description: `Status: ${this.currentStatus}`
            }
        ];

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Helios Actions'
        });

        if (selected) {
            if (selected.label.includes('Enable') || selected.label.includes('Disable')) {
                vscode.commands.executeCommand('helios.toggleAssistant');
            } else if (selected.label.includes('Restart')) {
                vscode.commands.executeCommand('helios.restartServer');
            } else if (selected.label.includes('Settings')) {
                vscode.commands.executeCommand('workbench.action.openSettings', 'helios');
            }
        }
    }

    dispose(): void {
        this.statusBarItem.dispose();
    }
}