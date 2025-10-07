import * as vscode from 'vscode';

export class HeliosLogger {
    private outputChannel: vscode.OutputChannel;
    private debugMode: boolean = false;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Helios');
        this.updateDebugMode();
        
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration(event => {
            if (event.affectsConfiguration('helios.debugMode')) {
                this.updateDebugMode();
            }
        });
    }

    private updateDebugMode(): void {
        const config = vscode.workspace.getConfiguration('helios');
        this.debugMode = config.get<boolean>('debugMode', false);
    }

    public info(message: string, data?: any): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[INFO] ${timestamp}: ${message}`;
        
        this.outputChannel.appendLine(logMessage);
        
        if (data) {
            this.outputChannel.appendLine(JSON.stringify(data, null, 2));
        }
        
        if (this.debugMode) {
            console.log(logMessage, data);
        }
    }

    public warn(message: string, data?: any): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[WARN] ${timestamp}: ${message}`;
        
        this.outputChannel.appendLine(logMessage);
        
        if (data) {
            this.outputChannel.appendLine(JSON.stringify(data, null, 2));
        }
        
        console.warn(logMessage, data);
    }

    public error(message: string, error?: any): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[ERROR] ${timestamp}: ${message}`;
        
        this.outputChannel.appendLine(logMessage);
        
        if (error) {
            if (error instanceof Error) {
                this.outputChannel.appendLine(`Stack: ${error.stack}`);
            } else {
                this.outputChannel.appendLine(JSON.stringify(error, null, 2));
            }
        }
        
        console.error(logMessage, error);
    }

    public debug(message: string, data?: any): void {
        if (!this.debugMode) {
            return;
        }
        
        const timestamp = new Date().toISOString();
        const logMessage = `[DEBUG] ${timestamp}: ${message}`;
        
        this.outputChannel.appendLine(logMessage);
        
        if (data) {
            this.outputChannel.appendLine(JSON.stringify(data, null, 2));
        }
        
        console.debug(logMessage, data);
    }

    public show(): void {
        this.outputChannel.show();
    }

    public clear(): void {
        this.outputChannel.clear();
    }

    public dispose(): void {
        this.outputChannel.dispose();
    }
}

// Singleton logger instance
export const logger = new HeliosLogger();