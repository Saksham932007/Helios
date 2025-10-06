import * as vscode from 'vscode';
import { HeliosCompletionProvider } from './completion';
import { HeliosStatusBar } from './statusBar';
import { HeliosTerminalManager } from './terminal';
import { HeliosServer } from './server';

let completionProvider: HeliosCompletionProvider;
let statusBar: HeliosStatusBar;
let terminalManager: HeliosTerminalManager;
let server: HeliosServer;

export function activate(context: vscode.ExtensionContext) {
    console.log('Helios extension is now active!');

    // Initialize components
    server = new HeliosServer();
    statusBar = new HeliosStatusBar();
    terminalManager = new HeliosTerminalManager();
    completionProvider = new HeliosCompletionProvider(server);

    // Register completion provider for supported languages
    const languages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust'];
    languages.forEach(language => {
        const provider = vscode.languages.registerInlineCompletionItemProvider(
            { language },
            completionProvider
        );
        context.subscriptions.push(provider);
    });

    // Register commands
    const toggleCommand = vscode.commands.registerCommand('helios.toggleAssistant', () => {
        const config = vscode.workspace.getConfiguration('helios');
        const enabled = config.get<boolean>('enabled', true);
        config.update('enabled', !enabled, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`Helios ${!enabled ? 'enabled' : 'disabled'}`);
    });

    const runFileCommand = vscode.commands.registerCommand('helios.runCurrentFile', () => {
        terminalManager.runCurrentFile();
    });

    const runSelectionCommand = vscode.commands.registerCommand('helios.runSelectedCode', () => {
        terminalManager.runSelectedCode();
    });

    const restartServerCommand = vscode.commands.registerCommand('helios.restartServer', () => {
        server.restart();
    });

    // Add to subscriptions
    context.subscriptions.push(
        toggleCommand,
        runFileCommand,
        runSelectionCommand,
        restartServerCommand,
        statusBar,
        server
    );

    // Initialize server connection
    server.initialize();
}

export function deactivate() {
    if (server) {
        server.dispose();
    }
}