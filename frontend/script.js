const API_BASE_URL = 'http://localhost:5003';

let selectedISBN = null;
let currentBookInfo = null;

async function searchRestaurants() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) {
        showError('検索クエリを入力してください');
        return;
    }

    showLoading(true);
    hideAllSections();

    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();
        showLoading(false);

        if (data.status === 'isbn_confirmed') {
            // ISBN確定の場合、書籍情報を表示
            selectedISBN = data.isbn;
            currentBookInfo = data.book_info;
            displayBookInfo(data.book_info);
        } else if (data.status === 'candidates_found') {
            // 候補が見つかった場合、候補リストを表示
            displayCandidates(data.candidates);
        } else {
            // 結果が見つからない場合
            showError(data.message || '該当する書籍が見つかりませんでした');
        }

    } catch (error) {
        showLoading(false);
        showError('検索中にエラーが発生しました: ' + error.message);
    }
}

function displayCandidates(candidates) {
    const candidatesSection = document.getElementById('candidates-section');
    const candidatesList = document.getElementById('candidates-list');
    
    candidatesList.innerHTML = '';
    
    candidates.forEach((candidate, index) => {
        const candidateDiv = document.createElement('div');
        candidateDiv.className = 'candidate-item';
        candidateDiv.onclick = () => selectCandidate(candidate, candidateDiv);
        
        candidateDiv.innerHTML = `
            <div class="book-display">
                <div class="book-cover">
                    ${candidate.cover_image ? 
                        `<img src="${candidate.cover_image}" alt="書影" onerror="this.style.display='none'">` : 
                        '<div style="width:80px;height:120px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:4px;"><span style="font-size:12px;color:#999;">書影なし</span></div>'
                    }
                </div>
                <div class="book-details">
                    <h3>${candidate.title}</h3>
                    <p><strong>著者:</strong> ${candidate.author}</p>
                    <p><strong>出版社:</strong> ${candidate.publisher || '不明'}</p>
                    <p><strong>ISBN:</strong> ${candidate.isbn}</p>
                </div>
            </div>
        `;
        
        candidatesList.appendChild(candidateDiv);
    });
    
    candidatesSection.classList.remove('hidden');
}

function selectCandidate(candidate, element) {
    // 既選択の候補から選択状態を削除
    document.querySelectorAll('.candidate-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // 新しい候補を選択状態に
    element.classList.add('selected');
    
    selectedISBN = candidate.isbn;
    currentBookInfo = candidate;
    
    // 書籍情報セクションを表示
    setTimeout(() => {
        displayBookInfo(candidate);
    }, 300);
}

function displayBookInfo(bookInfo) {
    const bookInfoSection = document.getElementById('book-info-section');
    const bookInfoDiv = document.getElementById('book-info');
    
    bookInfoDiv.innerHTML = `
        <div class="book-display">
            <div class="book-cover">
                ${bookInfo.cover_image ? 
                    `<img src="${bookInfo.cover_image}" alt="書影" onerror="this.style.display='none'">` : 
                    '<div style="width:120px;height:180px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:6px;"><span style="font-size:14px;color:#999;">書影なし</span></div>'
                }
            </div>
            <div class="book-details">
                <h3>${bookInfo.title || '書名不明'}</h3>
                <p><strong>著者:</strong> ${bookInfo.author || '不明'}</p>
                <p><strong>出版社:</strong> ${bookInfo.publisher || '不明'}</p>
                <p><strong>ISBN:</strong> ${selectedISBN}</p>
            </div>
        </div>
    `;
    
    bookInfoSection.classList.remove('hidden');
    
    // 候補セクションを隠す
    document.getElementById('candidates-section').classList.add('hidden');
}

async function comparePrices() {
    if (!selectedISBN) {
        showError('ISBNが選択されていません');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/price-comparison`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ isbn: selectedISBN }),
        });

        const data = await response.json();
        showLoading(false);

        if (data.price_comparison && data.price_comparison.length > 0) {
            displayPriceComparison(data.price_comparison);
        } else {
            showError('価格情報が見つかりませんでした');
        }

    } catch (error) {
        showLoading(false);
        showError('価格比較中にエラーが発生しました: ' + error.message);
    }
}

function displayPriceComparison(priceData) {
    const priceSection = document.getElementById('price-comparison-section');
    const priceTable = document.getElementById('price-comparison-table');
    
    let tableHTML = `
        <table class="price-table">
            <thead>
                <tr>
                    <th>サイト</th>
                    <th>本体価格</th>
                    <th>送料</th>
                    <th>合計金額</th>
                    <th>コンディション</th>
                    <th>在庫状況</th>
                    <th>リンク</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    priceData.forEach(item => {
        const rowClass = item.is_cheapest ? 'cheapest' : '';
        const stockClass = item.in_stock ? 'in-stock' : 'out-of-stock';
        const stockText = item.in_stock ? '在庫あり' : '在庫なし';
        
        tableHTML += `
            <tr class="${rowClass}">
                <td><strong>${item.site}</strong></td>
                <td class="price">¥${item.price.toLocaleString()}</td>
                <td>¥${item.shipping.toLocaleString()}</td>
                <td class="total-price">¥${item.total_price.toLocaleString()}</td>
                <td><span class="condition">${item.condition}</span></td>
                <td class="${stockClass}">${stockText}</td>
                <td><a href="${item.url}" target="_blank" class="site-link">商品ページ</a></td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    priceTable.innerHTML = tableHTML;
    priceSection.classList.remove('hidden');
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function hideAllSections() {
    document.getElementById('candidates-section').classList.add('hidden');
    document.getElementById('restaurant-info-section').classList.add('hidden');
    document.getElementById('price-comparison-section').classList.add('hidden');
    document.getElementById('error-section').classList.add('hidden');
}

function showError(message) {
    document.getElementById('error-text').textContent = message;
    document.getElementById('error-section').classList.remove('hidden');
}

function resetSearch() {
    document.getElementById('search-input').value = '';
    selectedISBN = null;
    currentBookInfo = null;
    hideAllSections();
}

// Enter キーで検索を実行
document.getElementById('search-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        searchRestaurants();
    }
});