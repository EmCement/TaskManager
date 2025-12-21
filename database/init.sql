DROP TABLE IF EXISTS attachment CASCADE;
DROP TABLE IF EXISTS comment CASCADE;
DROP TABLE IF EXISTS task_assignee CASCADE;
DROP TABLE IF EXISTS task CASCADE;
DROP TABLE IF EXISTS status CASCADE;
DROP TABLE IF EXISTS priority CASCADE;
DROP TABLE IF EXISTS project CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_role CHECK (role IN ('admin', 'manager', 'user'))
);

CREATE TABLE project (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_creator FOREIGN KEY (created_by) 
        REFERENCES "user"(id) ON DELETE SET NULL
);

CREATE TABLE priority (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 5),
    color VARCHAR(7) DEFAULT '#6B7280'
);

CREATE TABLE status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    order_num INTEGER DEFAULT 0,
    is_final BOOLEAN DEFAULT FALSE
);

CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    project_id INTEGER NOT NULL,
    priority_id INTEGER,
    status_id INTEGER,
    created_by INTEGER,
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_task_project FOREIGN KEY (project_id) 
        REFERENCES project(id) ON DELETE CASCADE,
    CONSTRAINT fk_task_priority FOREIGN KEY (priority_id) 
        REFERENCES priority(id) ON DELETE SET NULL,
    CONSTRAINT fk_task_status FOREIGN KEY (status_id) 
        REFERENCES status(id) ON DELETE SET NULL,
    CONSTRAINT fk_task_creator FOREIGN KEY (created_by) 
        REFERENCES "user"(id) ON DELETE SET NULL
);

CREATE TABLE task_assignee (
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, user_id),
    CONSTRAINT fk_assignee_task FOREIGN KEY (task_id) 
        REFERENCES task(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignee_user FOREIGN KEY (user_id) 
        REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id INTEGER,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comment_task FOREIGN KEY (task_id) 
        REFERENCES task(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_user FOREIGN KEY (user_id) 
        REFERENCES "user"(id) ON DELETE SET NULL
);

CREATE TABLE attachment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id INTEGER,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    size BIGINT,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attachment_task FOREIGN KEY (task_id) 
        REFERENCES task(id) ON DELETE CASCADE,
    CONSTRAINT fk_attachment_user FOREIGN KEY (user_id) 
        REFERENCES "user"(id) ON DELETE SET NULL
);

CREATE INDEX idx_task_project ON task(project_id);
CREATE INDEX idx_task_status ON task(status_id);
CREATE INDEX idx_task_priority ON task(priority_id);
CREATE INDEX idx_task_created_by ON task(created_by);
CREATE INDEX idx_task_due_date ON task(due_date);
CREATE INDEX idx_comment_task ON comment(task_id);
CREATE INDEX idx_attachment_task ON attachment(task_id);
CREATE INDEX idx_project_creator ON project(created_by);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_project_updated_at BEFORE UPDATE ON project
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_updated_at BEFORE UPDATE ON task
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comment_updated_at BEFORE UPDATE ON comment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO priority (name, level, color) VALUES
('Низкий', 1, '#10B981'),
('Средний', 2, '#F59E0B'),
('Высокий', 3, '#EF4444'),
('Критичный', 4, '#DC2626');

INSERT INTO status (name, order_num, is_final) VALUES
('Новая', 1, FALSE),
('В работе', 2, FALSE),
('На проверке', 3, FALSE),
('Завершена', 4, TRUE),
('Отменена', 5, TRUE);
