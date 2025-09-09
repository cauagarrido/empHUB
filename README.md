Backend da Plataforma empHUB 🚀
Este repositório contém o código-fonte do backend para a plataforma empHUB, uma aplicação web projetada para ser um hub central de comunicação e gestão de projetos para empresas, equipes e grupos.

A API é responsável por toda a lógica de negócio, incluindo autenticação de usuários, gerenciamento de grupos, manipulação de projetos e comunicação com o banco de dados.

✨ Funcionalidades Principais
Autenticação de Usuários: Sistema seguro de cadastro e login utilizando JWT (JSON Web Tokens).

Gerenciamento de Grupos:

Criação de grupos de trabalho (empresas/equipes).

Sistema de convite por código único de 8 dígitos, garantindo acesso controlado.

Gestão de Projetos (Kanban):

Criação, listagem e atualização de projetos.

Sistema de status (Novo Projeto, Em Desenvolvimento, Em Análise, Concluído) para simular um quadro Kanban.

Atribuição de um responsável para cada projeto.

🛠️ Stack Tecnológica
Backend: Python 3 com o framework Flask.

Banco de Dados: Supabase (PostgreSQL).

Autenticação: Supabase Auth para gerenciamento de usuários e JWT.

Frontend (Planejado): A API foi projetada para se comunicar com um frontend em React JS.
