import * as vscode from 'vscode';
import axios from 'axios';

export interface CompletionRequest {
    code: string;
    language: string;
    position: vscode.Position;
    filename: string;
}

export interface CompletionResponse {
    suggestion: string;
    confidence: number;
}

export class HeliosServer {
    private serverUrl: string;
    private isConnected: boolean = false;

    constructor() {
        this.serverUrl = vscode.workspace.getConfiguration('helios').get('serverUrl', 'http://localhost:8000');
    }

    async initialize(): Promise<void> {
        await this.checkConnection();
    }

    async checkConnection(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.serverUrl}/health`, { timeout: 5000 });
            this.isConnected = response.status === 200;
            return this.isConnected;
        } catch (error) {
            this.isConnected = false;
            return false;
        }
    }

    async getCompletion(request: CompletionRequest): Promise<CompletionResponse | null> {
        if (!this.isConnected) {
            const connected = await this.checkConnection();
            if (!connected) {
                return null;
            }
        }

        try {
            const response = await axios.post(`${this.serverUrl}/complete`, request, {
                timeout: 10000,
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            return response.data;
        } catch (error) {
            console.error('Error getting completion:', error);
            this.isConnected = false;
            return null;
        }
    }

    async restart(): Promise<void> {
        try {
            await axios.post(`${this.serverUrl}/restart`, {}, { timeout: 5000 });
            vscode.window.showInformationMessage('Helios server restarted successfully');
        } catch (error) {
            vscode.window.showErrorMessage('Failed to restart Helios server');
        }
    }

    isServerConnected(): boolean {
        return this.isConnected;
    }

    getServerUrl(): string {
        return this.serverUrl;
    }

    dispose(): void {
        // Cleanup if needed
    }
}