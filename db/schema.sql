-- =====================================================
-- Musdocemas
-- Esquema mínimo de base de datos (PostgreSQL)
-- =====================================================

CREATE TABLE IF NOT EXISTS usuarios (
  usuario_id SERIAL PRIMARY KEY,
  nombre_usuario VARCHAR(50),
  alias VARCHAR(50),
  email VARCHAR(100),
  password_hash VARCHAR(255),
  avatar_url VARCHAR(255),
  activo BOOLEAN,
  clave_activacion VARCHAR(6),
  fecha_registro TIMESTAMP WITHOUT TIME ZONE,
  codigo_activacion VARCHAR(6),
  verificado BOOLEAN
);

-- -----------------------------------------------------
-- Índices de unicidad (evitan duplicidades)
-- -----------------------------------------------------

-- Clave primaria (ya creada por PRIMARY KEY)
-- usuarios_pkey ON usuario_id

CREATE UNIQUE INDEX IF NOT EXISTS usuarios_alias_key
  ON public.usuarios USING btree (alias);

CREATE UNIQUE INDEX IF NOT EXISTS usuarios_email_key
  ON public.usuarios USING btree (email);
