import * as vscode from 'vscode';

export class HeliosKeybindingManager {
    private disposables: vscode.Disposable[] = [];

    constructor() {
        this.registerKeybindings();
    }

    private registerKeybindings(): void {
        // Tab to accept completion
        this.disposables.push(
            vscode.commands.registerCommand('helios.acceptCompletion', () => {
                this.handleAcceptCompletion();
            })
        );

        // Escape to dismiss completion
        this.disposables.push(
            vscode.commands.registerCommand('helios.dismissCompletion', () => {
                this.handleDismissCompletion();
            })
        );

        // Ctrl+Space to manually trigger completion
        this.disposables.push(
            vscode.commands.registerCommand('helios.triggerCompletion', () => {
                this.handleTriggerCompletion();
            })
        );

        // Ctrl+Shift+C to generate code from comment
        this.disposables.push(
            vscode.commands.registerCommand('helios.generateFromComment', () => {
                this.handleGenerateFromComment();
            })
        );
    }

    private handleAcceptCompletion(): void {
        // Get the completion manager from extension context
        const completionManager = this.getCompletionManager();
        if (completionManager) {
            const accepted = completionManager.acceptSuggestion();
            if (accepted) {
                vscode.window.showInformationMessage('Helios: Completion accepted', { modal: false });
            }
        }
    }

    private handleDismissCompletion(): void {
        const completionManager = this.getCompletionManager();
        if (completionManager) {
            completionManager.dismissSuggestion();
        }
    }

    private async handleTriggerCompletion(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        // Manually trigger completion
        await vscode.commands.executeCommand('editor.action.triggerSuggest');
    }

    private async handleGenerateFromComment(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const document = editor.document;
        const selection = editor.selection;
        let commentText = '';

        if (!selection.isEmpty) {
            // Use selected text as comment
            commentText = document.getText(selection);
        } else {
            // Use current line as comment
            const line = document.lineAt(selection.active.line);
            commentText = line.text.trim();
        }

        // Check if it looks like a comment
        const commentPatterns = [
            /^\/\/\s*(.+)$/,     // JavaScript/TypeScript //
            /^#\s*(.+)$/,        // Python #
            /^\/\*\s*(.+)\s*\*\/$/, // Multi-line comment
            /^\*\s*(.+)$/        // JSDoc style
        ];

        let isComment = false;
        for (const pattern of commentPatterns) {
            if (pattern.test(commentText)) {
                isComment = true;
                break;
            }
        }

        if (!isComment) {
            vscode.window.showWarningMessage('Selected text does not appear to be a comment');
            return;
        }

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating code from comment...',
            cancellable: false
        }, async (progress) => {
            try {
                // This would integrate with the completion system
                // For now, show a placeholder
                const generatedCode = await this.generateCodeFromComment(commentText, document.languageId);
                
                if (generatedCode) {
                    // Insert generated code after the comment
                    const insertPosition = selection.isEmpty ? 
                        new vscode.Position(selection.active.line + 1, 0) :
                        selection.end;
                    
                    await editor.edit(editBuilder => {
                        editBuilder.insert(insertPosition, '\n' + generatedCode);
                    });
                    
                    vscode.window.showInformationMessage('Code generated successfully!');
                } else {
                    vscode.window.showWarningMessage('Could not generate code from comment');
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Error generating code: ${error}`);
            }
        });
    }

    private async generateCodeFromComment(comment: string, language: string): Promise<string | null> {
        // This is a placeholder - in the real implementation, this would
        // use the inference server to generate code based on the comment
        
        // Simple template-based generation for demo
        const cleanComment = comment.replace(/^(\/\/|#|\*)\s*/, '').trim();
        
        if (language === 'python') {
            if (cleanComment.toLowerCase().includes('function')) {
                return `def generated_function():\n    """${cleanComment}"""\n    pass`;
            }
        } else if (language === 'javascript' || language === 'typescript') {
            if (cleanComment.toLowerCase().includes('function')) {
                return `function generatedFunction() {\n    // ${cleanComment}\n    // TODO: Implement\n}`;
            }
        }
        
        return `// Generated from: ${cleanComment}\n// TODO: Implement this functionality`;
    }

    private getCompletionManager(): any {
        // This would be injected or retrieved from the extension context
        // For now, return null as placeholder
        return null;
    }

    dispose(): void {
        this.disposables.forEach(d => d.dispose());
    }
}