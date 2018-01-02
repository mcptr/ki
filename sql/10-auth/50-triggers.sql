CREATE TRIGGER trg_adapt_user
       BEFORE INSERT OR UPDATE ON auth.users
       FOR EACH ROW EXECUTE PROCEDURE auth.trg_adapt_user();
