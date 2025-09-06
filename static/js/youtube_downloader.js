// YouTube Downloader JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('youtube-url');
    const downloadBtn = document.getElementById('download-btn');
    const loadingModal = document.getElementById('loading-modal');
    const resultModal = document.getElementById('result-modal');
    const resultContent = document.getElementById('result-content');
    const closeModal = document.getElementById('close-modal');
    
    // Event Listeners
    downloadBtn.addEventListener('click', handleDownload);
    closeModal.addEventListener('click', closeResultModal);
    
    // Allow Enter key to trigger download
    urlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleDownload();
        }
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === resultModal) {
            closeResultModal();
        }
    });
    
    // Handle download process
    async function handleDownload() {
        const url = urlInput.value.trim();
        const selectedFormat = document.querySelector('input[name="format"]:checked').value;
        
        // Validation
        if (!url) {
            showError('الرجاء إدخال رابط الفيديو');
            return;
        }
        
        if (!isValidYouTubeURL(url)) {
            showError('الرجاء إدخال رابط يوتيوب صحيح');
            return;
        }
        
        // Show loading modal
        showLoading();
        
        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    format: selectedFormat
                })
            });
            
            const data = await response.json();
            
            hideLoading();
            
            if (data.success) {
                showSuccess(data);
            } else {
                showError(data.error || 'حدث خطأ غير متوقع');
            }
            
        } catch (error) {
            hideLoading();
            showError('فشل في الاتصال بالخادم. يرجى المحاولة مرة أخرى.');
            console.error('Download error:', error);
        }
    }
    
    // Validate YouTube URL
    function isValidYouTubeURL(url) {
        const patterns = [
            /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
            /^https?:\/\/(www\.)?youtu\.be\/[\w-]+/,
            /^https?:\/\/(www\.)?youtube\.com\/embed\/[\w-]+/,
            /^https?:\/\/(www\.)?youtube\.com\/v\/[\w-]+/
        ];
        
        return patterns.some(pattern => pattern.test(url));
    }
    
    // Show loading modal
    function showLoading() {
        loadingModal.style.display = 'block';
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري التحميل...';
    }
    
    // Hide loading modal
    function hideLoading() {
        loadingModal.style.display = 'none';
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<i class="fas fa-download"></i> تحميل';
    }
    
    // Show success result
    function showSuccess(data) {
        resultContent.innerHTML = `
            <div class="success-message">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: #27ae60; margin-bottom: 20px;"></i>
                <h3>تم بنجاح!</h3>
                <p><strong>العنوان:</strong> ${data.title || 'غير محدد'}</p>
                <p>${data.message}</p>
                ${data.download_url ? `<a href="${data.download_url}" class="download-link" download>
                    <i class="fas fa-download"></i> تحميل الملف
                </a>` : ''}
            </div>
        `;
        showResultModal();
    }
    
    // Show error message
    function showError(message) {
        resultContent.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #e74c3c; margin-bottom: 20px;"></i>
                <h3>حدث خطأ</h3>
                <p>${message}</p>
                <button class="btn-primary" onclick="document.getElementById('result-modal').style.display='none'">
                    حسناً
                </button>
            </div>
        `;
        showResultModal();
    }
    
    // Show result modal
    function showResultModal() {
        resultModal.style.display = 'block';
    }
    
    // Close result modal
    function closeResultModal() {
        resultModal.style.display = 'none';
    }
    
    // URL Input Enhancement
    urlInput.addEventListener('input', function() {
        const url = this.value.trim();
        if (url && isValidYouTubeURL(url)) {
            this.style.borderColor = '#27ae60';
            downloadBtn.style.opacity = '1';
        } else if (url) {
            this.style.borderColor = '#e74c3c';
            downloadBtn.style.opacity = '0.7';
        } else {
            this.style.borderColor = '#e8f5e8';
            downloadBtn.style.opacity = '1';
        }
    });
    
    // Paste button functionality (if user wants to add it)
    function addPasteButton() {
        const pasteBtn = document.createElement('button');
        pasteBtn.innerHTML = '<i class="fas fa-paste"></i>';
        pasteBtn.className = 'paste-btn';
        pasteBtn.type = 'button';
        pasteBtn.title = 'لصق من الحافظة';
        
        pasteBtn.addEventListener('click', async function() {
            try {
                const text = await navigator.clipboard.readText();
                if (isValidYouTubeURL(text)) {
                    urlInput.value = text;
                    urlInput.dispatchEvent(new Event('input'));
                } else {
                    showError('الرابط المنسوخ ليس رابط يوتيوب صحيح');
                }
            } catch (err) {
                console.error('لا يمكن قراءة الحافظة:', err);
            }
        });
        
        // Add paste button to input group
        const inputGroup = document.querySelector('.input-group');
        inputGroup.insertBefore(pasteBtn, downloadBtn);
    }
    
    // Check if clipboard API is supported
    if (navigator.clipboard && navigator.clipboard.readText) {
        // Uncomment the next line if you want to add paste button
        // addPasteButton();
    }
    
    // Example URLs for testing
    const exampleUrls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtu.be/dQw4w9WgXcQ',
        'https://www.youtube.com/embed/dQw4w9WgXcQ'
    ];
    
    // Add example URL button for testing
    function addExampleButton() {
        const exampleBtn = document.createElement('button');
        exampleBtn.innerHTML = 'مثال';
        exampleBtn.className = 'btn-secondary';
        exampleBtn.type = 'button';
        exampleBtn.style.marginTop = '10px';
        
        exampleBtn.addEventListener('click', function() {
            const randomUrl = exampleUrls[Math.floor(Math.random() * exampleUrls.length)];
            urlInput.value = randomUrl;
            urlInput.dispatchEvent(new Event('input'));
        });
        
        document.querySelector('.download-form').appendChild(exampleBtn);
    }
    
    // Uncomment for development/testing
    // addExampleButton();
    
    // Format option enhancements
    const formatOptions = document.querySelectorAll('input[name="format"]');
    formatOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Update UI based on selected format
            const selectedLabel = this.closest('.radio-option');
            const allLabels = document.querySelectorAll('.radio-option');
            
            allLabels.forEach(label => {
                label.style.borderColor = '#e8f5e8';
                label.style.background = '#fafafa';
            });
            
            selectedLabel.style.borderColor = '#27ae60';
            selectedLabel.style.background = '#f0f8f0';
        });
    });
    
    // Auto-detect format based on URL (future enhancement)
    function detectOptimalFormat(url) {
        // This could be enhanced to suggest format based on video duration, etc.
        return 'mp4'; // Default
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + V to focus URL input
        if ((e.ctrlKey || e.metaKey) && e.key === 'v' && !e.target.matches('input, textarea')) {
            e.preventDefault();
            urlInput.focus();
        }
        
        // Escape to close modal
        if (e.key === 'Escape') {
            if (resultModal.style.display === 'block') {
                closeResultModal();
            }
        }
    });
    
    // Progress tracking (for future enhancement with real download progress)
    function updateProgress(percent) {
        // This function can be enhanced to show download progress
        console.log(`Download progress: ${percent}%`);
    }
    
    // Initialize format selection styling
    const defaultSelected = document.querySelector('input[name="format"]:checked');
    if (defaultSelected) {
        defaultSelected.dispatchEvent(new Event('change'));
    }
});