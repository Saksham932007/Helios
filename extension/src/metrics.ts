import * as vscode from 'vscode';

export interface PerformanceMetrics {
    completionRequests: number;
    successfulCompletions: number;
    failedCompletions: number;
    averageResponseTime: number;
    totalResponseTime: number;
    uptime: number;
    startTime: number;
}

export class HeliosMetricsCollector {
    private metrics: PerformanceMetrics;
    private responseTimes: number[] = [];
    private maxResponseTimeHistory = 100; // Keep last 100 response times

    constructor() {
        this.metrics = {
            completionRequests: 0,
            successfulCompletions: 0,
            failedCompletions: 0,
            averageResponseTime: 0,
            totalResponseTime: 0,
            uptime: 0,
            startTime: Date.now()
        };
    }

    public recordCompletionRequest(): void {
        this.metrics.completionRequests++;
    }

    public recordSuccessfulCompletion(responseTimeMs: number): void {
        this.metrics.successfulCompletions++;
        this.recordResponseTime(responseTimeMs);
    }

    public recordFailedCompletion(): void {
        this.metrics.failedCompletions++;
    }

    private recordResponseTime(timeMs: number): void {
        this.responseTimes.push(timeMs);
        
        // Keep only the last N response times
        if (this.responseTimes.length > this.maxResponseTimeHistory) {
            this.responseTimes.shift();
        }
        
        // Update metrics
        this.metrics.totalResponseTime += timeMs;
        this.metrics.averageResponseTime = this.responseTimes.reduce((a, b) => a + b, 0) / this.responseTimes.length;
    }

    public getMetrics(): PerformanceMetrics {
        this.metrics.uptime = Date.now() - this.metrics.startTime;
        return { ...this.metrics };
    }

    public getSuccessRate(): number {
        if (this.metrics.completionRequests === 0) {
            return 0;
        }
        return (this.metrics.successfulCompletions / this.metrics.completionRequests) * 100;
    }

    public getDetailedMetrics(): any {
        const basic = this.getMetrics();
        return {
            ...basic,
            successRate: this.getSuccessRate(),
            requestsPerMinute: this.getRequestsPerMinute(),
            medianResponseTime: this.getMedianResponseTime(),
            p95ResponseTime: this.getPercentileResponseTime(95),
            recentResponseTimes: this.responseTimes.slice(-10) // Last 10 response times
        };
    }

    private getRequestsPerMinute(): number {
        const uptimeMinutes = this.metrics.uptime / (1000 * 60);
        if (uptimeMinutes === 0) {
            return 0;
        }
        return this.metrics.completionRequests / uptimeMinutes;
    }

    private getMedianResponseTime(): number {
        if (this.responseTimes.length === 0) {
            return 0;
        }
        
        const sorted = [...this.responseTimes].sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        
        if (sorted.length % 2 === 0) {
            return (sorted[mid - 1] + sorted[mid]) / 2;
        } else {
            return sorted[mid];
        }
    }

    private getPercentileResponseTime(percentile: number): number {
        if (this.responseTimes.length === 0) {
            return 0;
        }
        
        const sorted = [...this.responseTimes].sort((a, b) => a - b);
        const index = Math.ceil((percentile / 100) * sorted.length) - 1;
        return sorted[Math.max(0, index)];
    }

    public reset(): void {
        this.metrics = {
            completionRequests: 0,
            successfulCompletions: 0,
            failedCompletions: 0,
            averageResponseTime: 0,
            totalResponseTime: 0,
            uptime: 0,
            startTime: Date.now()
        };
        this.responseTimes = [];
    }

    public exportMetrics(): string {
        const metrics = this.getDetailedMetrics();
        return JSON.stringify(metrics, null, 2);
    }

    public async showMetricsReport(): Promise<void> {
        const metrics = this.getDetailedMetrics();
        
        const report = `
# Helios Performance Report

## Summary
- **Total Requests**: ${metrics.completionRequests}
- **Successful**: ${metrics.successfulCompletions}
- **Failed**: ${metrics.failedCompletions}
- **Success Rate**: ${metrics.successRate.toFixed(1)}%
- **Uptime**: ${(metrics.uptime / 1000 / 60).toFixed(1)} minutes

## Response Times
- **Average**: ${metrics.averageResponseTime.toFixed(0)}ms
- **Median**: ${metrics.medianResponseTime.toFixed(0)}ms
- **95th Percentile**: ${metrics.p95ResponseTime.toFixed(0)}ms

## Throughput
- **Requests per Minute**: ${metrics.requestsPerMinute.toFixed(1)}

## Recent Response Times
${metrics.recentResponseTimes.map((time: number) => `${time}ms`).join(', ')}
        `;

        // Show in a new document
        const doc = await vscode.workspace.openTextDocument({
            content: report,
            language: 'markdown'
        });
        
        await vscode.window.showTextDocument(doc);
    }
}

// Singleton metrics collector
export const metricsCollector = new HeliosMetricsCollector();