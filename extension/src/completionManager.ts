import * as vscode from 'vscode';
import { HeliosServer } from './server';
import { ServerStatus } from './statusBar';

export class HeliosCompletionManager {
    private server: HeliosServer;
    private statusBar: any;
    private isProcessing: boolean = false;
    private lastSuggestion: string = '';
    private currentDocument: vscode.TextDocument | undefined;
    private currentPosition: vscode.Position | undefined;

    constructor(server: HeliosServer, statusBar: any) {
        this.server = server;
        this.statusBar = statusBar;
        this.setupEventListeners();
    }

    private setupEventListeners(): void {
        // Listen for text changes to trigger completions
        vscode.workspace.onDidChangeTextDocument(this.onTextChange.bind(this));
        
        // Listen for cursor position changes
        vscode.window.onDidChangeTextEditorSelection(this.onSelectionChange.bind(this));
        
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration(this.onConfigChange.bind(this));
    }

    private async onTextChange(event: vscode.TextDocumentChangeEvent): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document !== event.document) {
            return;
        }

        // Check if completion is enabled
        const config = vscode.workspace.getConfiguration('helios');
        if (!config.get<boolean>('enabled', true)) {
            return;
        }

        // Debounce rapid changes
        if (this.isProcessing) {
            return;
        }

        this.isProcessing = true;
        this.statusBar.setStatus(ServerStatus.Processing);

        try {
            await this.triggerCompletion(editor);
        } finally {
            this.isProcessing = false;
            this.statusBar.setStatus(ServerStatus.Idle);
        }
    }

    private onSelectionChange(event: vscode.TextEditorSelectionChangeEvent): void {
        // Clear suggestions when cursor moves significantly
        if (this.currentDocument && this.currentPosition) {
            const newPosition = event.textEditor.selection.active;
            const lineDiff = Math.abs(newPosition.line - this.currentPosition.line);
            const charDiff = Math.abs(newPosition.character - this.currentPosition.character);
            
            if (lineDiff > 0 || charDiff > 3) {
                this.clearSuggestion();
            }
        }
    }

    private onConfigChange(event: vscode.ConfigurationChangeEvent): void {
        if (event.affectsConfiguration('helios')) {
            // Restart server if URL changed
            if (event.affectsConfiguration('helios.serverUrl')) {
                this.server.restart();
            }
        }
    }

    private async triggerCompletion(editor: vscode.TextEditor): Promise<void> {
        const document = editor.document;
        const position = editor.selection.active;
        
        // Skip if we're in the middle of a word
        const line = document.lineAt(position);
        const charAfterCursor = position.character < line.text.length ? 
            line.text.charAt(position.character) : '';
        
        if (charAfterCursor && /\w/.test(charAfterCursor)) {
            return;
        }

        // Get context for completion
        const context = this.getCompletionContext(document, position);
        if (!context) {
            return;
        }

        try {
            const completion = await this.server.getCompletion(context);
            if (completion && completion.suggestion) {
                await this.showSuggestion(editor, position, completion.suggestion);
            }
        } catch (error) {
            console.error('Error getting completion:', error);
            this.statusBar.setStatus(ServerStatus.Error);
        }
    }

    private getCompletionContext(document: vscode.TextDocument, position: vscode.Position): any {
        // Get surrounding context
        const startLine = Math.max(0, position.line - 20);
        const endLine = Math.min(document.lineCount - 1, position.line + 5);
        
        const contextRange = new vscode.Range(
            new vscode.Position(startLine, 0),
            position
        );
        
        const contextText = document.getText(contextRange);
        
        return {
            code: contextText,
            language: document.languageId,
            position: { line: position.line, character: position.character },
            filename: document.fileName
        };
    }

    private async showSuggestion(
        editor: vscode.TextEditor, 
        position: vscode.Position, 
        suggestion: string
    ): Promise<void> {
        this.lastSuggestion = suggestion;
        this.currentDocument = editor.document;
        this.currentPosition = position;

        // Create a decoration to show the suggestion as ghost text
        const decorationType = vscode.window.createTextEditorDecorationType({
            after: {
                contentText: suggestion,
                color: new vscode.ThemeColor('editorSuggestWidget.foreground'),
                fontStyle: 'italic'
            }
        });

        // Apply decoration
        editor.setDecorations(decorationType, [new vscode.Range(position, position)]);

        // Auto-remove decoration after some time if not accepted
        setTimeout(() => {
            decorationType.dispose();
        }, 10000);
    }

    private clearSuggestion(): void {
        this.lastSuggestion = '';
        this.currentDocument = undefined;
        this.currentPosition = undefined;
    }

    public acceptSuggestion(): boolean {
        if (!this.lastSuggestion || !this.currentDocument || !this.currentPosition) {
            return false;
        }

        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document !== this.currentDocument) {
            return false;
        }

        // Insert the suggestion
        editor.edit(editBuilder => {
            editBuilder.insert(this.currentPosition!, this.lastSuggestion);
        });

        this.clearSuggestion();
        return true;
    }

    public dismissSuggestion(): void {
        this.clearSuggestion();
    }
}