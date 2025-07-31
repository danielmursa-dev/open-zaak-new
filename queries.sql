-- CREATE openzaak_new
DROP DATABASE openzaak_new;
CREATE DATABASE openzaak_new;
ALTER ROLE openzaak_new WITH SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS;
GRANT ALL PRIVILEGES ON DATABASE openzaak_new TO openzaak_new;

-- CREATE experiment
DROP DATABASE experiment;
CREATE DATABASE experiment;
ALTER ROLE experiment WITH SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS;
GRANT ALL PRIVILEGES ON DATABASE experiment TO experiment;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO experiment_entry (name) SELECT substr(encode(gen_random_bytes(8), 'hex'), 1, 35) FROM generate_series(1, 1000000);


-- FULL INSERT QUERY startig from TAG 0.0.24
CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO zaken_zaak (
    uuid,
    omschrijving,
    toelichting,
    betalingsindicatie,
    verlenging_reden,
    opschorting_reden,
    opschorting_indicatie,
    opschorting_eerdere_opschorting,
    archiefnominatie,
    archiefstatus,
    processobjectaard,
    processobject_datumkenmerk,
    processobject_identificatie,
    processobject_objecttype,
    processobject_registratie,
    communicatiekanaal_naam,
    registratiedatum,
    startdatum,
    einddatum,
    einddatum_gepland,
    uiterlijke_einddatum_afdoening,
    publicatiedatum,
    laatste_betaaldatum,
    archiefactiedatum,
    startdatum_bewaartermijn,
    created_on,
    verantwoordelijke_organisatie,
    opdrachtgevende_organisatie,
    zaakgeometrie,
    verlenging_duur,
    vertrouwelijkheidaanduiding,
    selectielijstklasse,
    communicatiekanaal,
    producten_of_diensten,
    identificatie,
    bronorganisatie
)
SELECT
    gen_random_uuid(), -- uuid
    substr(encode(gen_random_bytes(8), 'hex'), 1, 80), -- omschrijving
    substr(md5(random()::text), 1, 1000), -- toelichting
    'nog_niet', -- betalingsindicatie
    substr(md5(random()::text), 1, 200), -- verlenging_reden
    substr(md5(random()::text), 1, 200), -- opschorting_reden
    (random() < 0.5), -- opschorting_indicatie
    (random() < 0.5), -- opschorting_eerdere_opschorting
    'vernietigen', -- archiefnominatie
    substr(md5(random()::text), 1, 40), -- archiefstatus
    substr(md5(random()::text), 1, 200), -- processobjectaard
    substr(md5(random()::text), 1, 250), -- processobject_datumkenmerk
    substr(md5(random()::text), 1, 250), -- processobject_identificatie
    substr(md5(random()::text), 1, 250), -- processobject_objecttype
    substr(md5(random()::text), 1, 250), -- processobject_registratie
    substr(md5(random()::text), 1, 250), -- communicatiekanaal_naam
    current_date, -- registratiedatum
    current_date, -- startdatum
    current_date, -- einddatum
    current_date, -- einddatum_gepland
    current_date, -- uiterlijke_einddatum_afdoening
    current_date, -- publicatiedatum
    current_timestamp, -- laatste_betaaldatum
    current_date, -- archiefactiedatum
    current_date, -- startdatum_bewaartermijn
    current_timestamp, -- created_on
    '123456782', -- verantwoordelijke_organisatie
    '123456782', -- opdrachtgevende_organisatie
    NULL, -- zaakgeometrie
    interval '10 days' * floor(random() * 10), -- verlenging_duur
    'openbaar', -- vertrouwelijkheidaanduiding
    'https://example.com/selectielijstklasse', -- selectielijstklasse
    'https://example.com/communicatiekanaal', -- communicatiekanaal
    ARRAY[
        'https://example.com/product1',
        'https://example.com/product2'
    ], -- producten_of_diensten
    substr(md5(random()::text), 1, 40), -- identificatie
    '123456782' -- bronorganisatie
FROM generate_series(1, 1000000);


-- QUERY TO GENERATE THE FIRST 100 RELATIONSHIPS BETWEEN PARENTS AND CHILDREN ZAAKEN
WITH top_100 AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id DESC) AS rn
    FROM zaken_zaak
    WHERE hoofdzaak_id IS NULL
    ORDER BY id DESC
    LIMIT 100 
),
hoofdzaken AS (
    SELECT id
    FROM top_100
    WHERE rn <= 50
),
deelzaken AS (
    SELECT e.id AS deel_id, h.id AS hoofd_id
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY id DESC) AS rn
        FROM top_100
        WHERE rn > 50
    ) e
    JOIN LATERAL (
        SELECT id
        FROM hoofdzaken
        ORDER BY random()
        LIMIT 1
    ) h ON true
)
UPDATE zaken_zaak
SET hoofdzaak_id = deelzaken.hoofd_id
FROM deelzaken
WHERE zaken_zaak.id = deelzaken.deel_id;


-- QUERY TO GENERATE ZAAK_TYPE FOR ALL ZAKEN
INSERT INTO catalogi_zaaktype (uuid, identificatie)
SELECT
    gen_random_uuid(),
    'ZKT-' || LPAD(i::text, 4, '0') AS identificatie
FROM generate_series(1, 100) AS s(i);

DO $$
BEGIN
  FOR i IN 1..100 LOOP
    RAISE NOTICE 'i = %:', i;

    WITH geselecteerde_zaken AS (
        SELECT id
        FROM zaken_zaak
        WHERE _zaaktype_id IS NULL
        LIMIT 10000
    ),
    toewijzing AS (
        SELECT z.id AS zaak_id,
               (SELECT id FROM catalogi_zaaktype ORDER BY random() LIMIT 1) AS zaaktype_id
        FROM geselecteerde_zaken z
    )
    UPDATE zaken_zaak
    SET _zaaktype_id = toewijzing.zaaktype_id
    FROM toewijzing
    WHERE zaken_zaak.id = toewijzing.zaak_id;
  END LOOP;
END $$;


-- QUERY TO GENERATE ROLLEN
INSERT INTO zaken_rol (uuid, _etag, zaak_id, betrokkene_type)
SELECT gen_random_uuid(), md5('initiator'), z.id, 'medewerker'
FROM zaken_zaak z
LEFT JOIN zaken_rol r ON z.id = r.zaak_id
WHERE r.zaak_id IS NULL;