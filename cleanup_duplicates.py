from app import app, db
from models import ProgramaAcademico, Bolsista, Residente

with app.app_context():
    # Find duplicates: Same Code
    codes = db.session.query(ProgramaAcademico.codigo_programa).group_by(ProgramaAcademico.codigo_programa).having(db.func.count(ProgramaAcademico.id) > 1).all()
    
    deleted_count = 0
    
    for (code,) in codes:
        if not code: continue
        
        # Get all programs with this code
        progs = ProgramaAcademico.query.filter_by(codigo_programa=code).all()
        
        # Group by Campus ID to find true duplicates (Same Code + Same Campus)
        by_campus = {}
        for p in progs:
            cid = p.campus_id
            if cid not in by_campus: by_campus[cid] = []
            by_campus[cid].append(p)
            
        for cid, group in by_campus.items():
            if len(group) > 1:
                # We have duplicates in same campus!
                print(f"Found {len(group)} entries for code {code} in Campus {cid}")
                
                # Sort by usage (keep the one with most records)
                # Or if all 0, keep the one with lowest ID (original) or highest ID (newest)?
                # Let's keep the one with records. If equal, keep lowest ID.
                
                group_with_counts = []
                for p in group:
                    b = Bolsista.query.filter_by(programa_id=p.id).count()
                    r = Residente.query.filter_by(programa_id=p.id).count()
                    group_with_counts.append((p, b+r))
                
                # Sort descending by count, then ascending by ID
                group_with_counts.sort(key=lambda x: (-x[1], x[0].id))
                
                keep = group_with_counts[0][0]
                to_delete = group_with_counts[1:]
                
                print(f"  Keeping ID {keep.id} ({keep.nome_programa}) - Records: {group_with_counts[0][1]}")
                
                for p_del, count in to_delete:
                    if count > 0:
                        print(f"  SKIPPING deletion of ID {p_del.id} because it has {count} records. Manual merge needed.")
                    else:
                        print(f"  DELETING ID {p_del.id} ({p_del.nome_programa}) - Records: 0")
                        db.session.delete(p_del)
                        deleted_count += 1
                        
    if deleted_count > 0:
        db.session.commit()
        print(f"\nSuccessfully deleted {deleted_count} duplicate programs.")
    else:
        print("\nNo safe deletions performed.")
