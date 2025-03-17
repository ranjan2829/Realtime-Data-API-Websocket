// src/server.ts
import express from 'express';
import path from 'path';
import fs from 'fs';
import Groq from 'groq-sdk';

// Simple vector store implementation
class SimpleVectorStore {
    private documents: string[] = [];
    private embeddings: number[][] = [];

    constructor(documentsPath: string) {
        this.initialize(documentsPath);
    }

    private initialize(documentsPath: string) {
        if (!fs.existsSync(documentsPath)) {
            fs.writeFileSync(documentsPath, 
                "Retrieval-Augmented Generation (RAG) is a technique that combines retrieval of relevant information with generation of responses. " +
                "It uses a vector store to find relevant context and then generates answers based on that context."
            );
        }
        const content = fs.readFileSync(documentsPath, 'utf-8');
        this.addDocument(content);
    }

    private generateEmbedding(text: string): number[] {
        const words = text.toLowerCase().split(/\s+/);
        const embedding = new Array(100).fill(0);
        for (let i = 0; i < Math.min(words.length, 100); i++) {
            embedding[i] = Math.abs(this.hashString(words[i]) % 100);
        }
        return embedding;
    }

    private hashString(str: string): number {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = (hash << 5) - hash + str.charCodeAt(i);
            hash = hash & hash;
        }
        return hash;
    }

    addDocument(text: string) {
        this.documents.push(text);
        this.embeddings.push(this.generateEmbedding(text));
    }

    getRelevantContext(query: string): string {
        const queryEmbedding = this.generateEmbedding(query);
        const similarities = this.embeddings.map((embedding, index) => ({
            index,
            similarity: this.cosineSimilarity(queryEmbedding, embedding)
        }));

        similarities.sort((a, b) => b.similarity - a.similarity);
        const topDocs = similarities.slice(0, 2).map(sim => this.documents[sim.index]);
        return topDocs.join('\n');
    }

    private cosineSimilarity(vecA: number[], vecB: number[]): number {
        const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
        const magA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
        const magB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
        return magA && magB ? dotProduct / (magA * magB) : 0;
    }
}

// Groq Service
class GroqService {
    private client: Groq;

    constructor() {
        this.client = new Groq({ 
            apiKey: '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'
        });
    }

    async generateResponse(query: string, context: string): Promise<string> {
        const prompt = `As Grok, created by xAI, I'll help you with this query using the provided context.\n` +
                      `Context: ${context}\n` +
                      `Query: ${query}\n` +
                      `Answer: `;

        try {
            const chatCompletion = await this.client.chat.completions.create({
                messages: [{ role: 'user', content: prompt }],
                model: 'mixtral-8x7b-32768',
                max_tokens: 200
            });
            const choice = chatCompletion.choices[0];
            if (choice && choice.message && choice.message.content) {
                return choice.message.content.trim();
            }
            return "No response generated";
        } catch (error) {
            return `Error: ${(error as Error).message}`;
        }
    }
}

// Express Server
const app = express();
const PORT = 3000;
const documentsPath = path.join(__dirname, '../knowledge_base.txt');
const vectorStore = new SimpleVectorStore(documentsPath);
const groqService = new GroqService();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/query', async (req, res) => {
    try {
        const query = req.query.q as string;
        if (!query) {
            return res.status(400).json({ error: 'Query parameter is required' });
        }
        const context = vectorStore.getRelevantContext(query);
        const response = await groqService.generateResponse(query, context);
        res.json({ response });
    } catch (error) {
        res.status(500).json({ error: 'Error processing query' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});