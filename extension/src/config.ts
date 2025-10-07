import * as vscode from 'vscode';

export interface HeliosSettings {
    enabled: boolean;
    serverUrl: string;
    modelPath: string;
    maxTokens: number;
    temperature: number;
    autoComplete: boolean;
    commentToCode: boolean;
    debugMode: boolean;
    completionDelay: number;
    showNotifications: boolean;
}

export class HeliosConfigManager {
    private config: vscode.WorkspaceConfiguration;
    private onConfigChangedEmitter = new vscode.EventEmitter<HeliosSettings>();
    public readonly onConfigChanged = this.onConfigChangedEmitter.event;

    constructor() {
        this.config = vscode.workspace.getConfiguration('helios');
        
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration(event => {
            if (event.affectsConfiguration('helios')) {
                this.config = vscode.workspace.getConfiguration('helios');
                this.onConfigChangedEmitter.fire(this.getSettings());
            }
        });
    }

    public getSettings(): HeliosSettings {
        return {
            enabled: this.config.get<boolean>('enabled', true),
            serverUrl: this.config.get<string>('serverUrl', 'http://localhost:8000'),
            modelPath: this.config.get<string>('modelPath', ''),
            maxTokens: this.config.get<number>('maxTokens', 100),
            temperature: this.config.get<number>('temperature', 0.1),
            autoComplete: this.config.get<boolean>('autoComplete', true),
            commentToCode: this.config.get<boolean>('commentToCode', true),
            debugMode: this.config.get<boolean>('debugMode', false),
            completionDelay: this.config.get<number>('completionDelay', 300),
            showNotifications: this.config.get<boolean>('showNotifications', true)
        };
    }

    public async updateSetting<K extends keyof HeliosSettings>(
        key: K, 
        value: HeliosSettings[K],
        target: vscode.ConfigurationTarget = vscode.ConfigurationTarget.Global
    ): Promise<void> {
        await this.config.update(key, value, target);
    }

    public async resetToDefaults(): Promise<void> {
        const defaultSettings: HeliosSettings = {
            enabled: true,
            serverUrl: 'http://localhost:8000',
            modelPath: '',
            maxTokens: 100,
            temperature: 0.1,
            autoComplete: true,
            commentToCode: true,
            debugMode: false,
            completionDelay: 300,
            showNotifications: true
        };

        for (const [key, value] of Object.entries(defaultSettings)) {
            await this.updateSetting(key as keyof HeliosSettings, value);
        }

        vscode.window.showInformationMessage('Helios settings reset to defaults');
    }

    public async openSettingsUI(): Promise<void> {
        await vscode.commands.executeCommand('workbench.action.openSettings', 'helios');
    }

    public async validateConfiguration(): Promise<boolean> {
        const settings = this.getSettings();
        const issues: string[] = [];

        // Validate server URL
        try {
            new URL(settings.serverUrl);
        } catch {
            issues.push('Invalid server URL format');
        }

        // Validate numeric ranges
        if (settings.maxTokens < 1 || settings.maxTokens > 2048) {
            issues.push('Max tokens should be between 1 and 2048');
        }

        if (settings.temperature < 0 || settings.temperature > 1) {
            issues.push('Temperature should be between 0 and 1');
        }

        if (settings.completionDelay < 0 || settings.completionDelay > 5000) {
            issues.push('Completion delay should be between 0 and 5000ms');
        }

        // Validate model path if specified
        if (settings.modelPath && !settings.modelPath.endsWith('.gguf')) {
            issues.push('Model path should point to a .gguf file');
        }

        if (issues.length > 0) {
            const message = `Configuration issues found:\n${issues.join('\n')}`;
            vscode.window.showWarningMessage(message, 'Open Settings').then(selection => {
                if (selection === 'Open Settings') {
                    this.openSettingsUI();
                }
            });
            return false;
        }

        return true;
    }

    public getConfigurationSchema(): any {
        return {
            type: 'object',
            title: 'Helios Configuration',
            properties: {
                'helios.enabled': {
                    type: 'boolean',
                    default: true,
                    description: 'Enable/disable Helios code completion'
                },
                'helios.serverUrl': {
                    type: 'string',
                    default: 'http://localhost:8000',
                    description: 'URL of the local inference server',
                    format: 'uri'
                },
                'helios.modelPath': {
                    type: 'string',
                    default: '',
                    description: 'Path to the CodeLlama model file (.gguf format)'
                },
                'helios.maxTokens': {
                    type: 'number',
                    default: 100,
                    minimum: 1,
                    maximum: 2048,
                    description: 'Maximum number of tokens to generate'
                },
                'helios.temperature': {
                    type: 'number',
                    default: 0.1,
                    minimum: 0,
                    maximum: 1,
                    description: 'Temperature for code generation (0 = deterministic, 1 = creative)'
                },
                'helios.autoComplete': {
                    type: 'boolean',
                    default: true,
                    description: 'Enable automatic code completion while typing'
                },
                'helios.commentToCode': {
                    type: 'boolean',
                    default: true,
                    description: 'Enable comment-to-code generation'
                },
                'helios.debugMode': {
                    type: 'boolean',
                    default: false,
                    description: 'Enable debug logging and verbose output'
                },
                'helios.completionDelay': {
                    type: 'number',
                    default: 300,
                    minimum: 0,
                    maximum: 5000,
                    description: 'Delay in milliseconds before triggering completion'
                },
                'helios.showNotifications': {
                    type: 'boolean',
                    default: true,
                    description: 'Show status notifications'
                }
            }
        };
    }

    dispose(): void {
        this.onConfigChangedEmitter.dispose();
    }
}