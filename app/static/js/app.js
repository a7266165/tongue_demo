function app() {
    return {
        // State
        wsConnected: false,
        dragover: false,
        processing: false,
        sessionId: '',
        steps: [],
        resultImages: {},
        analysisResults: {},
        ws: null,

        // WebSocket
        initWebSocket() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${location.host}/ws/live`;

            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.wsConnected = true;
                console.log('WebSocket connected');
            };

            this.ws.onclose = () => {
                this.wsConnected = false;
                console.log('WebSocket disconnected, reconnecting in 3s...');
                setTimeout(() => this.initWebSocket(), 3000);
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWsMessage(data);
            };
        },

        handleWsMessage(data) {
            if (data.type === 'step_complete') {
                // Update step status
                const step = this.steps.find(s => s.name === data.step);
                if (step) {
                    step.status = 'done';
                }
                // Add image if provided
                if (data.image) {
                    this.resultImages[data.step] = data.image;
                }
            } else if (data.type === 'pipeline_done') {
                this.processing = false;
                if (data.results) {
                    this.analysisResults = data.results;
                }
            }
        },

        // File handling
        handleDrop(event) {
            this.dragover = false;
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFiles(files);
            }
        },

        handleFiles(event) {
            const files = event.target.files;
            if (files.length > 0) {
                this.uploadFiles(files);
            }
        },

        async uploadFiles(files) {
            this.processing = true;
            this.resultImages = {};
            this.analysisResults = {};
            this.sessionId = '';

            // Set up progress steps
            this.steps = [
                { name: 'classify', label: '分類正反面', status: 'pending' },
                { name: 'mask', label: '舌頭遮罩', status: 'pending' },
                { name: 'white_balance', label: '白平衡校正', status: 'pending' },
            ];

            const formData = new FormData();
            for (const file of files) {
                formData.append('files', file);
            }

            try {
                // Mark first step as running
                this.steps[0].status = 'running';

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();

                if (data.error) {
                    alert(data.error);
                    this.processing = false;
                    return;
                }

                this.sessionId = data.session_id;
                this.resultImages = data.images || {};
                this.analysisResults = data.results || {};

                // Mark all steps as done
                this.steps.forEach(s => s.status = 'done');
            } catch (err) {
                console.error('Upload failed:', err);
                alert('上傳失敗，請確認伺服器是否啟動');
            }

            this.processing = false;
        },

        // Helpers
        formatImageLabel(key) {
            const labels = {
                'front': '正面',
                'back': '反面',
                'masked': '遮罩',
            };
            let result = key;
            for (const [eng, zh] of Object.entries(labels)) {
                result = result.replace(eng, zh);
            }
            return result.replace(/_/g, ' ');
        },

        formatStepName(key) {
            const names = {
                'classify': '正反面分類',
                'mask': '遮罩',
                'white_balance': '白平衡',
            };
            return names[key] || key;
        },
    };
}
