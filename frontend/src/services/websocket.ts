import { useEffect, useState, useCallback, useRef } from 'react';
import { WeatherData } from '@/types';

export interface WebSocketMessage {
  type: 'weather_update' | 'alert' | 'status' | 'heartbeat' | 'error';
  data: any;
  timestamp: string;
}

export interface WebSocketOptions {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private reconnectAttempts = 0;
  private heartbeatInterval: number;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageListeners: ((message: WebSocketMessage) => void)[] = [];
  private connectionListeners: ((connected: boolean) => void)[] = [];

  constructor(options: WebSocketOptions) {
    this.url = options.url;
    this.reconnectInterval = options.reconnectInterval || 5000;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
    this.heartbeatInterval = options.heartbeatInterval || 30000;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.notifyConnectionListeners(true);
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.notifyMessageListeners(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket closed');
          this.notifyConnectionListeners(false);
          this.stopHeartbeat();
          this.attemptReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  subscribe(callback: (message: WebSocketMessage) => void): () => void {
    this.messageListeners.push(callback);
    return () => {
      this.messageListeners = this.messageListeners.filter((cb) => cb !== callback);
    };
  }

  onConnectionChange(callback: (connected: boolean) => void): () => void {
    this.connectionListeners.push(callback);
    return () => {
      this.connectionListeners = this.connectionListeners.filter(
        (cb) => cb !== callback
      );
    };
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private notifyMessageListeners(message: WebSocketMessage): void {
    this.messageListeners.forEach((listener) => {
      try {
        listener(message);
      } catch (error) {
        console.error('Error in message listener:', error);
      }
    });
  }

  private notifyConnectionListeners(connected: boolean): void {
    this.connectionListeners.forEach((listener) => {
      try {
        listener(connected);
      } catch (error) {
        console.error('Error in connection listener:', error);
      }
    });
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping' });
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(
          `Attempting reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
        );
        this.connect().catch((error) => {
          console.error('Reconnect failed:', error);
        });
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts exceeded');
    }
  }
}

export const useWebSocket = (url: string) => {
  const clientRef = useRef<WebSocketClient | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const client = new WebSocketClient({
      url,
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
    });
    clientRef.current = client;

    client.connect().catch((err) => {
      setError(err.message);
    });

    const unsubscribeMessage = client.subscribe((message) => {
      setLastMessage(message);
      setError(null);
    });

    const unsubscribeConnection = client.onConnectionChange((isConnected) => {
      setConnected(isConnected);
    });

    return () => {
      unsubscribeMessage();
      unsubscribeConnection();
      client.disconnect();
    };
  }, [url]);

  const send = useCallback((message: any) => {
    if (clientRef.current) {
      clientRef.current.send(message);
    }
  }, []);

  const subscribe = useCallback((callback: (message: WebSocketMessage) => void) => {
    if (clientRef.current) {
      return clientRef.current.subscribe(callback);
    }
    return () => {};
  }, []);

  return {
    connected,
    lastMessage,
    error,
    send,
    subscribe,
  };
};
