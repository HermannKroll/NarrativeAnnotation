-- Remove all 'newentry' genes
DELETE FROM public.Predication AS p
WHERE (p.subject_id = 'newentry' and p.subject_type = 'Gene') OR (p.object_id = 'newentry' and p.object_type = 'Gene');

-- Update Dosage Form
-- UPDATE public.Predication SET relation = 'administered' WHERE subject_type = 'DosageForm' or object_type = 'DosageForm';

-- Update Method and LabMethod relation
-- UPDATE public.Predication SET relation = 'method' WHERE subject_type = 'Method' or object_type = 'Method';
-- UPDATE public.Predication SET relation = 'method' WHERE subject_type = 'LabMethod' or object_type = 'LabMethod';

-- Delete all symmetric predications (subject = object)
DELETE FROM public.Predication AS p WHERE p.subject_id = p.object_id and p.subject_type = p.object_type;

-- DELETE NER things
DELETE FROM public.Predication AS p where p.subject_id = '-' or p.object_id = '-';

-- PathIE associated relations can now
UPDATE public.Predication SET relation = null WHERE extraction_type = 'PathIE' and relation = 'associated';
-- Delete associations that were extracted from PathIE
DELETE public.Predication WHERE relation IS NULL and extraction_type = 'PathIE';
-- Ensure that all predication based on co-occurrences are mapped to associated
UPDATE public.Predication SET relation = 'associated' WHERE relation is NULL and extraction_type = 'COSentence';
-- Update all non-relations
UPDATE public.Predication SET relation = 'associated' WHERE relation IS NULL;
