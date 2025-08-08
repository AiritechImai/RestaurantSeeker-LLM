const API_BASE_URL = 'http://localhost:5003';

let selectedRestaurantId = null;
let currentRestaurantInfo = null;

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

        if (data.status === 'restaurants_found') {
            // レストランが見つかった場合、候補リストを表示
            displayCandidates(data.restaurants);
        } else {
            // 結果が見つからない場合
            showError(data.message || '該当するレストランが見つかりませんでした');
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
        
        // 評価を星で表示
        const stars = '★'.repeat(Math.floor(candidate.rating || 0)) + '☆'.repeat(5 - Math.floor(candidate.rating || 0));
        
        // 特徴をタグとして表示
        const featuresHTML = candidate.features ? 
            candidate.features.map(feature => `<span class="feature-tag">${feature}</span>`).join('') : '';
        
        candidateDiv.innerHTML = `
            <div class="restaurant-display">
                <div class="restaurant-image">
                    ${candidate.image ? 
                        `<img src="${candidate.image}" alt="レストラン画像" onerror="this.style.display='none'">` : 
                        '<div style="width:120px;height:90px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:4px;"><span style="font-size:12px;color:#999;">画像なし</span></div>'
                    }
                </div>
                <div class="restaurant-details">
                    <h3>${candidate.name}</h3>
                    <p><strong>料理ジャンル:</strong> ${candidate.cuisine}</p>
                    <p><strong>エリア:</strong> ${candidate.location}</p>
                    <p><strong>評価:</strong> ${stars} ${candidate.rating || '-'}</p>
                    <p><strong>価格帯:</strong> ${candidate.price_range || '-'}</p>
                    <p class="restaurant-description">${candidate.description || ''}</p>
                    <div class="features">${featuresHTML}</div>
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
    
    selectedRestaurantId = candidate.id;
    currentRestaurantInfo = candidate;
    
    // レストラン情報セクションを表示
    setTimeout(() => {
        displayRestaurantInfo(candidate);
    }, 300);
}

function displayRestaurantInfo(restaurantInfo) {
    const restaurantInfoSection = document.getElementById('restaurant-info-section');
    const restaurantInfoDiv = document.getElementById('restaurant-info');
    
    // 評価を星で表示
    const stars = '★'.repeat(Math.floor(restaurantInfo.rating || 0)) + '☆'.repeat(5 - Math.floor(restaurantInfo.rating || 0));
    
    // 特徴をタグとして表示
    const featuresHTML = restaurantInfo.features ? 
        restaurantInfo.features.map(feature => `<span class="feature-tag">${feature}</span>`).join('') : '';
    
    restaurantInfoDiv.innerHTML = `
        <div class="restaurant-display">
            <div class="restaurant-image">
                ${restaurantInfo.image ? 
                    `<img src="${restaurantInfo.image}" alt="レストラン画像" onerror="this.style.display='none'">` : 
                    '<div style="width:200px;height:150px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:6px;"><span style="font-size:14px;color:#999;">画像なし</span></div>'
                }
            </div>
            <div class="restaurant-details">
                <h3>${restaurantInfo.name || 'レストラン名不明'}</h3>
                <p><strong>料理ジャンル:</strong> ${restaurantInfo.cuisine || '不明'}</p>
                <p><strong>エリア:</strong> ${restaurantInfo.location || '不明'}</p>
                <p><strong>住所:</strong> ${restaurantInfo.address || '不明'}</p>
                <p><strong>電話番号:</strong> ${restaurantInfo.phone || '不明'}</p>
                <p><strong>評価:</strong> ${stars} ${restaurantInfo.rating || '-'}</p>
                <p><strong>価格帯:</strong> ${restaurantInfo.price_range || '-'}</p>
                <p class="restaurant-description">${restaurantInfo.description || ''}</p>
                <div class="features">${featuresHTML}</div>
            </div>
        </div>
    `;
    
    restaurantInfoSection.classList.remove('hidden');
    
    // 候補セクションを隠す
    document.getElementById('candidates-section').classList.add('hidden');
}

async function comparePrices() {
    if (!selectedRestaurantId) {
        showError('レストランが選択されていません');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/price-comparison`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ restaurant_id: selectedRestaurantId }),
        });

        const data = await response.json();
        showLoading(false);

        if (data.price_comparison && data.price_comparison.length > 0) {
            displayPriceComparison(data.price_comparison);
        } else {
            showError('価格・予約情報が見つかりませんでした');
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
                    <th>価格帯</th>
                    <th>予約可否</th>
                    <th>特徴</th>
                    <th>リンク</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    priceData.forEach(item => {
        const reservationClass = item.reservation_available ? 'reservation-available' : 'reservation-unavailable';
        const reservationText = item.reservation_available ? '予約可' : '情報のみ';
        
        // 特徴をタグとして表示
        const featuresHTML = item.features ? 
            item.features.map(feature => `<span class="site-feature-tag">${feature}</span>`).join('') : '';
        
        tableHTML += `
            <tr>
                <td><strong>${item.site}</strong></td>
                <td class="price-info">${item.price_info || '-'}</td>
                <td class="${reservationClass}">${reservationText}</td>
                <td class="features">${featuresHTML}</td>
                <td><a href="${item.url}" target="_blank" class="site-link">詳細を見る</a></td>
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
    selectedRestaurantId = null;
    currentRestaurantInfo = null;
    hideAllSections();
}

// Enter キーで検索を実行
document.getElementById('search-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        searchRestaurants();
    }
});