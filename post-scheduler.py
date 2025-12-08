#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📄 GERADOR DE POSTS + AGENDADOR

Gera sugestões de posts do dia (humanizados),
você escolhe quais postar e os horários!
"""

import os
import json
from datetime import datetime, time
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    print("❌ Erro: OPENAI_API_KEY não configurada!")
    exit(1)

llm = OpenAI(api_key=OPENAI_KEY, temperature=0.8, model="gpt-3.5-turbo")

# ============================================
# GERAR SUGESTÕES DE POSTS
# ============================================

def gerar_posts_do_dia(num_posts=5):
    """
    Gera sugestões de posts sobre sports + crypto
    com legendas humanizadas e trending topics
    """
    
    prompt = PromptTemplate(
        input_variables=["num"],
        template="""
Vocé é um especialista em conteúdo para crypto e sports.

Gere {num} sugestões de tweets HUMANIZADOS para hoje que:
- Foquem em oportunidades no Polymarket (sports + crypto)
- Sejam engajadores e naturais (não robóticos)
- NÃO terminem com perguntas
- Mencionem @Polymarket ou tendências do dia
- Tenham emojis relevantes
- Sejam concisos (<280 caracteres)

Retorne em JSON com este formato:
{{
  "posts": [
    {{
      "id": 1,
      "titulo": "Tema do post",
      "texto": "O tweet aqui",
      "categoria": "sports" ou "crypto"
    }}
  ]
}}
"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"num": num_posts})
    
    try:
        # Extrair JSON da resposta
        json_str = response.split('{')[1]
        json_str = '{' + json_str.split('}')[0] + '}'
        return json.loads(json_str)
    except:
        return None

# ============================================
# INTERFACE INTERATIVA
# ============================================

def main():
    print("\n" + "="*60)
    print("📄 GERADOR DE POSTS + AGENDADOR")
    print("="*60)
    print("\n🌟 Gerando 5 sugestões de posts para hoje...\n")
    
    # Gerar posts
    dados = gerar_posts_do_dia(5)
    
    if not dados:
        print("❌ Erro ao gerar posts. Tente novamente.")
        return
    
    posts = dados.get('posts', [])
    selecionados = []
    
    # Mostrar opções
    print("\n" + "="*60)
    print("SUGESTÕES DO DIA:")
    print("="*60)
    
    for post in posts:
        print(f"\n[{post['id']}] {post['titulo']}")
        print(f"    Categoria: {post['categoria']}")
        print(f"    Tweet: {post['texto']}")
        print(f"    Carácteres: {len(post['texto'])}")
    
    # Escolher posts
    print("\n" + "="*60)
    print("SELEÇÃO:")
    print("="*60)
    
    while True:
        escolha = input("\n👤 Quais posts quer postar? (ex: 1,3,5 ou 'todos' ou 'sair'): ").strip().lower()
        
        if escolha == 'sair':
            print("\n👋 Até logo!")
            return
        
        if escolha == 'todos':
            selecionados = posts
            break
        
        try:
            ids = [int(x.strip()) for x in escolha.split(',')]
            selecionados = [p for p in posts if p['id'] in ids]
            if selecionados:
                break
        except:
            pass
        
        print("❌ Opção inválida. Tente novamente.")
    
    # Agendar horários
    print("\n" + "="*60)
    print(f"AGENDAMENTO ({len(selecionados)} posts):")
    print("="*60)
    
    agendamentos = []
    horarios_sugeridos = ["09:00", "12:00", "17:00"]
    
    for i, post in enumerate(selecionados):
        horario_sugerido = horarios_sugeridos[i] if i < len(horarios_sugeridos) else "18:00"
        
        print(f"\n📄 Post {i+1}: {post['titulo']}")
        horario = input(f"   Horário (padrão {horario_sugerido}): ").strip()
        
        if not horario:
            horario = horario_sugerido
        
        agendamentos.append({
            "titulo": post['titulo'],
            "texto": post['texto'],
            "categoria": post['categoria'],
            "horario": horario
        })
    
    # Resumo final
    print("\n" + "="*60)
    print("📄 RESUMO DOS AGENDAMENTOS:")
    print("="*60)
    
    for i, agd in enumerate(agendamentos, 1):
        print(f"\n{i}. [{agd['horario']}] {agd['titulo']}")
        print(f"   Tweet: {agd['texto'][:60]}...")
    
    confirmar = input("\n✅ Confirmar agendamentos? (s/n): ").strip().lower()
    
    if confirmar == 's':
        # Salvar em arquivo
        with open('posts_agendados.json', 'w', encoding='utf-8') as f:
            json.dump({
                "data": datetime.now().isoformat(),
                "posts": agendamentos
            }, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Posts agendados com sucesso!")
        print("   Arquivo: posts_agendados.json")
        print("\n🚧 Próximo passo: Executar o bot para postar nos horários")
    else:
        print("\n❌ Agendamento cancelado.")

if __name__ == "__main__":
    main()
