import * as vscode from 'vscode';
import { HeliosServer, CompletionRequest } from './server';

export class HeliosCompletionProvider implements vscode.InlineCompletionItemProvider {
    private server: HeliosServer;
    private lastCompletionTime: number = 0;
    private debounceDelay: number = 300; // ms

    constructor(server: HeliosServer) {
        this.server = server;
    }

    async provideInlineCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.InlineCompletionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionItem[] | vscode.InlineCompletionList | null> {
        
        // Check if Helios is enabled
        const config = vscode.workspace.getConfiguration('helios');
        if (!config.get<boolean>('enabled', true) || !config.get<boolean>('autoComplete', true)) {
            return null;
        }

        // Debounce rapid calls
        const now = Date.now();
        if (now - this.lastCompletionTime < this.debounceDelay) {
            return null;
        }
        this.lastCompletionTime = now;

        // Get context around cursor
        const line = document.lineAt(position);
        const textBeforeCursor = document.getText(new vscode.Range(
            new vscode.Position(Math.max(0, position.line - 10), 0),
            position
        ));

        // Skip if we're in the middle of a word
        const charAfterCursor = position.character < line.text.length ? 
            line.text.charAt(position.character) : '';
        if (charAfterCursor && /\w/.test(charAfterCursor)) {
            return null;
        }

        // Prepare completion request
        const request: CompletionRequest = {
            code: textBeforeCursor,
            language: document.languageId,
            position: position,
            filename: document.fileName
        };

        try {
            const completion = await this.server.getCompletion(request);
            if (!completion || !completion.suggestion) {
                return null;
            }

            // Create inline completion item
            const completionItem = new vscode.InlineCompletionItem(
                completion.suggestion,
                new vscode.Range(position, position)
            );

            return [completionItem];
        } catch (error) {
            console.error('Error in completion provider:', error);
            return null;
        }
    }

    /**
     * Detect if user has written a comment that should generate code
     */
    async detectCommentToCode(
        document: vscode.TextDocument,
        position: vscode.Position
    ): Promise<string | null> {
        const config = vscode.workspace.getConfiguration('helios');
        if (!config.get<boolean>('commentToCode', true)) {
            return null;
        }

        const line = document.lineAt(position);
        const trimmedLine = line.text.trim();
        
        // Detect various comment patterns
        const commentPatterns = [
            /^\/\/\s*(.+)$/, // JavaScript/TypeScript //
            /^#\s*(.+)$/,    // Python #
            /^\/\*\s*(.+)\s*\*\/$/, // Multi-line comment
        ];

        for (const pattern of commentPatterns) {
            const match = trimmedLine.match(pattern);
            if (match && match[1].length > 20) { // Only for descriptive comments
                return match[1];
            }
        }

        return null;
    }
}