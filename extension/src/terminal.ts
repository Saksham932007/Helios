import * as vscode from 'vscode';
import * as path from 'path';

export class HeliosTerminalManager {
    private terminal: vscode.Terminal | undefined;

    constructor() {
        // Clean up terminals when VS Code closes
        vscode.window.onDidCloseTerminal(closedTerminal => {
            if (this.terminal === closedTerminal) {
                this.terminal = undefined;
            }
        });
    }

    private getOrCreateTerminal(): vscode.Terminal {
        if (!this.terminal || this.terminal.exitStatus !== undefined) {
            this.terminal = vscode.window.createTerminal({
                name: 'Helios Terminal',
                iconPath: new vscode.ThemeIcon('robot')
            });
        }
        return this.terminal;
    }

    async runCurrentFile(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active file to run');
            return;
        }

        const document = editor.document;
        if (document.isUntitled) {
            vscode.window.showErrorMessage('Please save the file before running');
            return;
        }

        // Save the file first
        await document.save();

        const filePath = document.fileName;
        const fileName = path.basename(filePath);
        const fileExt = path.extname(filePath).toLowerCase();
        const terminal = this.getOrCreateTerminal();

        terminal.show();

        // Get the command based on file type
        const command = this.getRunCommand(filePath, fileExt);
        if (command) {
            terminal.sendText(`echo "Running ${fileName}..."`);
            terminal.sendText(command);
        } else {
            vscode.window.showErrorMessage(`Unsupported file type: ${fileExt}`);
        }
    }

    async runSelectedCode(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showErrorMessage('No code selected');
            return;
        }

        const selectedText = editor.document.getText(selection);
        const languageId = editor.document.languageId;
        const terminal = this.getOrCreateTerminal();

        terminal.show();

        // Handle different languages for code execution
        switch (languageId) {
            case 'python':
                terminal.sendText('python3 << EOF');
                terminal.sendText(selectedText);
                terminal.sendText('EOF');
                break;
            case 'javascript':
            case 'typescript':
                terminal.sendText('node << EOF');
                terminal.sendText(selectedText);
                terminal.sendText('EOF');
                break;
            case 'bash':
            case 'sh':
                terminal.sendText(selectedText);
                break;
            default:
                vscode.window.showWarningMessage(`Selected code execution not supported for ${languageId}`);
                break;
        }
    }

    private getRunCommand(filePath: string, fileExt: string): string | null {
        const fileName = path.basename(filePath);
        const dirPath = path.dirname(filePath);

        switch (fileExt) {
            case '.py':
                return `cd "${dirPath}" && python3 "${fileName}"`;
            case '.js':
                return `cd "${dirPath}" && node "${fileName}"`;
            case '.ts':
                return `cd "${dirPath}" && npx ts-node "${fileName}"`;
            case '.java':
                const className = path.basename(fileName, '.java');
                return `cd "${dirPath}" && javac "${fileName}" && java "${className}"`;
            case '.cpp':
            case '.cc':
            case '.cxx':
                const exeName = path.basename(fileName, fileExt);
                return `cd "${dirPath}" && g++ "${fileName}" -o "${exeName}" && ./"${exeName}"`;
            case '.c':
                const cExeName = path.basename(fileName, '.c');
                return `cd "${dirPath}" && gcc "${fileName}" -o "${cExeName}" && ./"${cExeName}"`;
            case '.go':
                return `cd "${dirPath}" && go run "${fileName}"`;
            case '.rs':
                return `cd "${dirPath}" && rustc "${fileName}" && ./"${path.basename(fileName, '.rs')}"`;
            case '.sh':
            case '.bash':
                return `cd "${dirPath}" && bash "${fileName}"`;
            case '.rb':
                return `cd "${dirPath}" && ruby "${fileName}"`;
            case '.php':
                return `cd "${dirPath}" && php "${fileName}"`;
            default:
                return null;
        }
    }

    dispose(): void {
        if (this.terminal) {
            this.terminal.dispose();
        }
    }
}