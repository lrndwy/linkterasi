from apps.models.baseModel import JENJANG_CHOICES
from apps.models.penggajianModel import penggajian, JENIS_CHOICES as JENIS_CHOICES_PENGGAJIAN
import pandas as pd
import csv
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from apps.models.mainModel import master as master_model, master_ekstrakulikuler as master_ekstrakulikuler_model
import logging

logger = logging.getLogger(__name__)



def total_siswa_sd(queryset):
    return sum(item.jumlah_siswa_kelas_1 or 0 + item.jumlah_siswa_kelas_2 or 0 + item.jumlah_siswa_kelas_3 or 0 + 
               item.jumlah_siswa_kelas_4 or 0 + item.jumlah_siswa_kelas_5 or 0 + item.jumlah_siswa_kelas_6 or 0 
               for item in queryset.filter(jenjang='SD'))

def total_siswa_smp(queryset):
    return sum(item.jumlah_siswa_kelas_7 or 0 + item.jumlah_siswa_kelas_8 or 0 + item.jumlah_siswa_kelas_9 or 0 
               for item in queryset.filter(jenjang='SMP'))

def total_siswa_sma(queryset):
    return sum(item.jumlah_siswa_kelas_10 or 0 + item.jumlah_siswa_kelas_11 or 0 + item.jumlah_siswa_kelas_12 or 0 
               for item in queryset.filter(jenjang='SMA'))

def total_siswa_smk(queryset):
    return sum(item.jumlah_siswa_kelas_10_smk or 0 + item.jumlah_siswa_kelas_11_smk or 0 + item.jumlah_siswa_kelas_12_smk or 0 
               for item in queryset.filter(jenjang='SMK'))

def total_siswa_tk(queryset):
    return sum(item.jumlah_siswa_tk or 0 
              for item in queryset.filter(jenjang='TK'))

def func_total_siswa_per_jenjang(daftar_sekolah):
    total_siswa_per_jenjang = {jenjang: 0 for jenjang, _ in JENJANG_CHOICES}
    for sekolah in daftar_sekolah:
        jenjang = sekolah.jenjang
        if jenjang in total_siswa_per_jenjang:
            if jenjang == 'TK':
                total_siswa = sekolah.jumlah_siswa_tk or 0
            else:
                total_siswa = sum(getattr(sekolah, f'jumlah_siswa_kelas_{i}', 0) or 0 for i in range(1, 13))
                total_siswa += sum(getattr(sekolah, f'jumlah_siswa_kelas_{i}_smk', 0) or 0 for i in range(10, 13))
            total_siswa_per_jenjang[jenjang] += total_siswa
    return total_siswa_per_jenjang

def func_total_sekolah_per_jenjang(model_master):
    return {
        jenjang: model_master.objects.filter(jenjang=jenjang).count()
        for jenjang, _ in JENJANG_CHOICES
    }

def total_pengeluaran_per_jenis():
    return {
        jenis: sum(
            sum(getattr(p, bulan) or 0 for bulan in ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'])
            for p in penggajian.objects.filter(karyawan__jenis=jenis)
        )
        for jenis, _ in JENIS_CHOICES_PENGGAJIAN
    }

def total_pengeluaran_per_bulan():
    bulan_fields = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember']
    return {
        bulan: sum(penggajian.objects.values_list(bulan, flat=True))
        for bulan in bulan_fields
    }

def total_pengeluaran():
    return sum(
        sum(getattr(p, bulan) or 0 for bulan in ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'])
        for p in penggajian.objects.all()
    )


def impor_data_customer(file):
    try:
        # Cek ekstensi file
        if file.name.endswith('.csv'):
            # Tambahkan parameter encoding='utf-8-sig' untuk menangani BOM
            data = pd.read_csv(file, 
                             encoding='utf-8-sig',
                             quoting=csv.QUOTE_ALL, 
                             escapechar='\\',
                             na_values=['', '-', 'nan'],  # Menangani nilai kosong
                             keep_default_na=True)
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file, na_values=['', '-'])
        else:
            raise ValidationError("Format file tidak didukung. Harap unggah file CSV atau Excel.")

        # Bersihkan nama kolom
        data.columns = data.columns.str.strip().str.lower()
        
        for index, row in data.iterrows():
            try:
                # Skip baris yang tidak memiliki nama sekolah
                if pd.isna(row.get('nama_sekolah')):
                    continue
                    
                master_instance = master_model(
                    no_mou=row.get('no_mou') if pd.notna(row.get('no_mou')) else None,
                    nama_yayasan=row.get('nama_yayasan') if pd.notna(row.get('nama_yayasan')) else None,
                    kepala_yayasan=row.get('kepala_yayasan') if pd.notna(row.get('kepala_yayasan')) else None,
                    nama_sekolah=row.get('nama_sekolah'),
                    nama_kepsek=row.get('nama_kepsek') if pd.notna(row.get('nama_kepsek')) else None,
                    provinsi_id=row.get('provinsi_id') if pd.notna(row.get('provinsi_id')) else None,
                    jenjang=row.get('jenjang'),
                    awal_kerjasama=pd.to_datetime(row.get('awal_kerjasama')).date() if pd.notna(row.get('awal_kerjasama')) else None,
                    akhir_kerjasama=pd.to_datetime(row.get('akhir_kerjasama')).date() if pd.notna(row.get('akhir_kerjasama')) else None,
                    jenis_kerjasama=row.get('jenis_kerjasama') if pd.notna(row.get('jenis_kerjasama')) else None,
                    jenis_produk=row.get('jenis_produk') if pd.notna(row.get('jenis_produk')) else None,
                    pembayaran=row.get('pembayaran') if pd.notna(row.get('pembayaran')) else None,
                    harga_buku=row.get('harga_buku') if pd.notna(row.get('harga_buku')) else None,
                    jumlah_komputer=row.get('jumlah_komputer') if pd.notna(row.get('jumlah_komputer')) else None,
                    jumlah_siswa_tk=row.get('jumlah_siswa_tk') if pd.notna(row.get('jumlah_siswa_tk')) else None,
                )
                
                # Set jumlah siswa untuk setiap kelas
                for i in range(1, 13):
                    value = row.get(f'jumlah_siswa_kelas_{i}')
                    setattr(master_instance, f'jumlah_siswa_kelas_{i}', 
                           int(value) if pd.notna(value) else None)
                
                # Set jumlah siswa SMK
                for i in range(10, 13):
                    value = row.get(f'jumlah_siswa_kelas_{i}_smk')
                    setattr(master_instance, f'jumlah_siswa_kelas_{i}_smk', 
                           int(value) if pd.notna(value) else None)
                
                master_instance.save()
            except Exception as e:
                logger.error(f"Error pada baris {index + 2}: {str(e)}")
                raise ValidationError(f"Error pada baris {index + 2}: {str(e)}")

        return True, "Data customer berhasil diimpor"
    except pd.errors.ParserError as e:
        logger.error(f"Gagal mengimpor data: Kesalahan format CSV. {str(e)}")
        return False, f"Gagal mengimpor data: Kesalahan format CSV. {str(e)}"
    except Exception as e:
        logger.error(f"Gagal mengimpor data: {str(e)}")
        return False, f"Gagal mengimpor data: {str(e)}"

def impor_data_customer_ekskul(file):
    try:
        # Cek ekstensi file
        if file.name.endswith('.csv'):
            # Tambahkan parameter on_bad_lines='skip' untuk menangani baris yang bermasalah
            data = pd.read_csv(file, 
                             quoting=csv.QUOTE_ALL, 
                             escapechar='\\',
                             on_bad_lines='skip',  # Menambahkan parameter ini
                             encoding='utf-8')  # Menentukan encoding secara eksplisit
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file)
        else:
            raise ValidationError("Format file tidak didukung. Harap unggah file CSV atau Excel.")

        # Bersihkan nama kolom
        data.columns = data.columns.str.strip().str.lower()
        
        # Daftar kolom yang diharapkan
        expected_columns = [
            'no_mou', 'nama_yayasan', 'kepala_yayasan', 'nama_sekolah', 
            'nama_kepsek', 'provinsi_id', 'jenjang', 'awal_kerjasama', 
            'akhir_kerjasama', 'jenis_kerjasama', 'jenis_produk', 'pembayaran',
            'harga_buku', 'jumlah_komputer', 'tipe_sekolah', 'jumlah_siswa_tk'
        ]
        
        # Tambahkan kolom jumlah siswa
        for i in range(1, 13):
            expected_columns.append(f'jumlah_siswa_kelas_{i}')
        for i in range(10, 13):
            expected_columns.append(f'jumlah_siswa_kelas_{i}_smk')

        # Periksa kolom yang ada
        missing_columns = [col for col in expected_columns if col not in data.columns]
        if missing_columns:
            raise ValidationError(f"Kolom berikut tidak ditemukan dalam file: {', '.join(missing_columns)}")

        # Proses setiap baris data
        for index, row in data.iterrows():
            try:
                master_ekskul = master_ekstrakulikuler_model(
                    no_mou=str(row.get('no_mou', '')),
                    nama_yayasan=str(row.get('nama_yayasan', '')),
                    kepala_yayasan=str(row.get('kepala_yayasan', '')),
                    nama_sekolah=str(row.get('nama_sekolah', '')),
                    nama_kepsek=str(row.get('nama_kepsek', '')),
                    provinsi_id=row.get('provinsi_id'),
                    jenjang=str(row.get('jenjang', '')),
                    awal_kerjasama=pd.to_datetime(row.get('awal_kerjasama')).date() if pd.notna(row.get('awal_kerjasama')) else None,
                    akhir_kerjasama=pd.to_datetime(row.get('akhir_kerjasama')).date() if pd.notna(row.get('akhir_kerjasama')) else None,
                    jenis_kerjasama=str(row.get('jenis_kerjasama', '')),
                    jenis_produk=str(row.get('jenis_produk', '')),
                    pembayaran=str(row.get('pembayaran', '')),
                    harga_buku=str(row.get('harga_buku', '')),
                    jumlah_komputer=row.get('jumlah_komputer'),
                    tipe_sekolah=str(row.get('tipe_sekolah', '')),
                    jumlah_siswa_tk=row.get('jumlah_siswa_tk'),
                )
                
                # Set jumlah siswa untuk setiap kelas
                for i in range(1, 13):
                    field_name = f'jumlah_siswa_kelas_{i}'
                    value = row.get(field_name)
                    if pd.notna(value):
                        try:
                            setattr(master_ekskul, field_name, int(value))
                        except (ValueError, TypeError):
                            setattr(master_ekskul, field_name, None)
                    else:
                        setattr(master_ekskul, field_name, None)

                for i in range(10, 13):
                    field_name = f'jumlah_siswa_kelas_{i}_smk'
                    value = row.get(field_name)
                    if pd.notna(value):
                        try:
                            setattr(master_ekskul, field_name, int(value))
                        except (ValueError, TypeError):
                            setattr(master_ekskul, field_name, None)
                    else:
                        setattr(master_ekskul, field_name, None)
                
                master_ekskul.save()
            except Exception as e:
                raise ValidationError(f"Error pada baris {index + 2}: {str(e)}")

        return True, "Data customer ekstrakulikuler berhasil diimpor"
    except pd.errors.ParserError as e:
        return False, f"Gagal mengimpor data: Format file tidak valid. Pastikan format sesuai template. Detail: {str(e)}"
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Gagal mengimpor data: {str(e)}"

def func_total_komputer_per_jenjang(daftar_sekolah):
    total_komputer_per_jenjang = {jenjang: 0 for jenjang, _ in JENJANG_CHOICES}
    for sekolah in daftar_sekolah:
        jenjang = sekolah.jenjang
        if jenjang in total_komputer_per_jenjang:
            total_komputer_per_jenjang[jenjang] += sekolah.jumlah_komputer or 0
    return total_komputer_per_jenjang
