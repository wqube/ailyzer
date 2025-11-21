<template>
    <div>
    <section class="hero">
      <div class="container">
        <div class="hero-content">
            <h2>Наймите лучших кандидатов с помощью AI</h2>
            <p>AIlyzer помогает работодателям находить идеальных сотрудников с помощью искусственного интеллекта</p>
            <div class="hero-buttons">

            <button @click="$emit('navigate', 'registration')" class="btn btn-primary btn-large"> Начать сейчас </button>
          
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
    export default{
        name: 'MainPage',
        emits: ['navigate'],
        methods: {
        navigateTo(page) {
            this.$emit('navigate', page);
        }
    }
    }
</script>