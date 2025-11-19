<template>
    <div>
        <section class="hero">
            <div class="container">
                <div class="hero-content">
                    <h2>Наймите лучших кандидатов с помощью AI</h2>
                    <p>AIlyzer помогает работодателям находить идеальных сотрудников с помощью искусственного интеллекта</p>
                    <div class="hero-buttons">
                        <button @click="navigateToRegistration" class="btn btn-primary btn-large">
                            Начать сейчас
                        </button>
                    </div>
                </div>

                <div class="hero-image">
                    <div class="placeholder-image">Иллюстрация AI анализа</div>
                </div>
            </div>
        </section>

        <section id="features" class="features">
            <div class="container">
                <h2>Преимущества для работодателей</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3>Анализ резюме</h3>
                        <p>Автоматический анализ и ранжирование кандидатов по релевантности</p>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🔍</div>
                        <h3>Поиск талантов</h3>
                        <p>Находите подходящих кандидатов в нашей базе резюме</p>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3>Экономия времени</h3>
                        <p>Сократите время на подбор персонала до 70%</p>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script>
export default {
    name: 'MainPageView',
    methods: {
        navigateToRegistration() {
            this.$router.push('/employer/register');
        }
    }
}
</script>

<style scoped>
/* Стили из оригинального MainPage.vue */
.hero {
    padding: 4rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.hero .container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    align-items: center;
}

.hero-content h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.hero-content p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
}

.btn-large {
    padding: 1rem 2rem;
    font-size: 1.1rem;
}

.hero-image {
    display: flex;
    justify-content: center;
    align-items: center;
}

.placeholder-image {
    width: 300px;
    height: 200px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed rgba(255, 255, 255, 0.3);
}

.features {
    padding: 4rem 0;
    background: #f8f9fa;
}

.features h2 {
    text-align: center;
    margin-bottom: 3rem;
    font-size: 2rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.feature-card h3 {
    margin-bottom: 1rem;
    color: #333;
}

.feature-card p {
    color: #666;
    line-height: 1.6;
}

@media (max-width: 768px) {
    .hero .container {
        grid-template-columns: 1fr;
        text-align: center;
    }
    
    .hero-content h2 {
        font-size: 2rem;
    }
}
</style>