from apps.models.baseModel import JENJANG_CHOICES
from apps.models.penggajianModel import penggajian, JENIS_CHOICES as JENIS_CHOICES_PENGGAJIAN
import pandas as pd
import csv
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from apps.models.mainModel import master as master_model, master_ekstrakulikuler as master_ekstrakulikuler_model, produk as produk_model, teknisi as teknisi_model, sales as sales_model
import logging
from datetime import datetime

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
            total_siswa = sekolah.jumlah_siswa_tk or 0
            total_siswa += sum(getattr(sekolah, f'jumlah_siswa_kelas_{i}', 0) or 0 for i in range(1, 13))
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
            data = pd.read_csv(file, 
                             encoding='utf-8-sig',
                             quoting=csv.QUOTE_ALL, 
                             escapechar='\\',
                             na_values=['', '-', 'nan'],
                             keep_default_na=True)
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file, na_values=['', '-'])
        else:
            raise ValidationError("Format file tidak didukung. Harap unggah file CSV atau Excel.")

        # Daftar kolom yang diharapkan sesuai CSV
        expected_columns = [
            'No MOU', 'Nama Yayasan', 'Kepala Yayasan', 'Nama Sekolah',
            'Nama Kepsek', 'Provinsi', 'Jenjang', 'Awal Kerjasama', 'Akhir Kerjasama',
            'Jenis Kerjasama', 'Jenis Produk', 'Pembayaran', 'Harga Buku',
            'User Produk', 'User Teknisi', 'User Sales', 'Jumlah Siswa TK'
        ]
        
        # Tambahkan kolom jumlah siswa
        for i in range(1, 13):
            expected_columns.append(f'Jumlah Siswa Kelas {i}')
        for i in range(10, 13):
            expected_columns.append(f'Jumlah Siswa Kelas {i} SMK')
        expected_columns.append('Jumlah Komputer')
        
        # Periksa kolom yang ada
        missing_columns = [col for col in expected_columns if col not in data.columns]
        if missing_columns:
            raise ValidationError(f"Kolom berikut tidak ditemukan dalam file: {', '.join(missing_columns)}")

        for index, row in data.iterrows():
            try:
                # Skip baris yang tidak memiliki nama sekolah
                if pd.isna(row.get('Nama Sekolah')):
                    continue

                # Cari user berdasarkan nama
                user_produk = None
                user_teknisi = None
                user_sales = None

                if pd.notna(row.get('User Produk')):
                    user_produk = produk_model.objects.filter(nama=row.get('User Produk')).first()
                if pd.notna(row.get('User Teknisi')):
                    user_teknisi = teknisi_model.objects.filter(nama=row.get('User Teknisi')).first()
                if pd.notna(row.get('User Sales')):
                    user_sales = sales_model.objects.filter(nama=row.get('User Sales')).first()

                # Konversi format tanggal
                def parse_date(date_str):
                    if pd.notna(date_str):
                        try:
                            return datetime.strptime(str(date_str), '%d/%m/%Y').date()
                        except ValueError:
                            return None
                    return None

                master_instance = master_model(
                    no_mou=row.get('No MOU') if pd.notna(row.get('No MOU')) else None,
                    nama_yayasan=row.get('Nama Yayasan') if pd.notna(row.get('Nama Yayasan')) else None,
                    kepala_yayasan=row.get('Kepala Yayasan') if pd.notna(row.get('Kepala Yayasan')) else None,
                    nama_sekolah=row.get('Nama Sekolah'),
                    nama_kepsek=row.get('Nama Kepsek') if pd.notna(row.get('Nama Kepsek')) else None,
                    provinsi=row.get('Provinsi') if pd.notna(row.get('Provinsi')) else None,
                    jenjang=row.get('Jenjang'),
                    awal_kerjasama=parse_date(row.get('Awal Kerjasama')),
                    akhir_kerjasama=parse_date(row.get('Akhir Kerjasama')),
                    jenis_kerjasama=row.get('Jenis Kerjasama').lower() if pd.notna(row.get('Jenis Kerjasama')) else None,
                    jenis_produk=row.get('Jenis Produk').lower() if pd.notna(row.get('Jenis Produk')) else None,
                    pembayaran=row.get('Pembayaran') if pd.notna(row.get('Pembayaran')) else None,
                    harga_buku=row.get('Harga Buku') if pd.notna(row.get('Harga Buku')) else None,
                    jumlah_siswa_tk=row.get('Jumlah Siswa TK') if pd.notna(row.get('Jumlah Siswa TK')) else None,
                    jumlah_komputer=row.get('Jumlah Komputer') if pd.notna(row.get('Jumlah Komputer')) else None,
                    user_produk=user_produk,
                    user_teknisi=user_teknisi,
                    user_sales=user_sales
                )

                # Set jumlah siswa untuk setiap kelas
                for i in range(1, 13):
                    col_name = f'Jumlah Siswa Kelas {i}'
                    value = row.get(col_name)
                    if pd.notna(value):
                        try:
                            setattr(master_instance, f'jumlah_siswa_kelas_{i}', int(value))
                        except (ValueError, TypeError):
                            setattr(master_instance, f'jumlah_siswa_kelas_{i}', None)
                    else:
                        setattr(master_instance, f'jumlah_siswa_kelas_{i}', None)

                # Set jumlah siswa SMK
                for i in range(10, 13):
                    col_name = f'Jumlah Siswa Kelas {i} SMK'
                    value = row.get(col_name)
                    if pd.notna(value):
                        try:
                            setattr(master_instance, f'jumlah_siswa_kelas_{i}_smk', int(value))
                        except (ValueError, TypeError):
                            setattr(master_instance, f'jumlah_siswa_kelas_{i}_smk', None)
                    else:
                        setattr(master_instance, f'jumlah_siswa_kelas_{i}_smk', None)

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
            data = pd.read_csv(file, 
                             encoding='utf-8-sig',
                             quoting=csv.QUOTE_ALL, 
                             escapechar='\\',
                             na_values=['', '-', 'nan'],
                             keep_default_na=True)
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file, na_values=['', '-'])
        else:
            raise ValidationError("Format file tidak didukung. Harap unggah file CSV atau Excel.")

        # Kolom yang wajib ada
        required_columns = ['Nama Sekolah', 'Jenjang']
        
        # Periksa kolom wajib
        missing_required = [col for col in required_columns if col not in data.columns]
        if missing_required:
            raise ValidationError(f"Kolom wajib berikut tidak ditemukan dalam file: {', '.join(missing_required)}")

        # Proses setiap baris data
        for index, row in data.iterrows():
            try:
                # Skip baris yang tidak memiliki nama sekolah
                if pd.isna(row.get('Nama Sekolah')):
                    continue

                # Cari user berdasarkan nama
                user_produk = None


                if pd.notna(row.get('User Produk')):
                    user_produk = produk_model.objects.filter(nama=row.get('User Produk')).first()
  

                # Konversi format tanggal
                def parse_date(date_str):
                    if pd.notna(date_str):
                        try:
                            return datetime.strptime(str(date_str), '%d/%m/%Y').date()
                        except ValueError:
                            return None
                    return None

                master_ekskul = master_ekstrakulikuler_model(
                    no_mou=row.get('No MOU') if 'No MOU' in data.columns and pd.notna(row.get('No MOU')) else None,
                    nama_yayasan=row.get('Nama Yayasan') if 'Nama Yayasan' in data.columns and pd.notna(row.get('Nama Yayasan')) else None,
                    kepala_yayasan=row.get('Kepala Yayasan') if 'Kepala Yayasan' in data.columns and pd.notna(row.get('Kepala Yayasan')) else None,
                    nama_sekolah=row.get('Nama Sekolah'),
                    nama_kepsek=row.get('Nama Kepsek') if 'Nama Kepsek' in data.columns and pd.notna(row.get('Nama Kepsek')) else None,
                    provinsi=row.get('Provinsi') if 'Provinsi' in data.columns and pd.notna(row.get('Provinsi')) else None,
                    jenjang=row.get('Jenjang'),
                    awal_kerjasama=parse_date(row.get('Awal Kerjasama')) if 'Awal Kerjasama' in data.columns else None,
                    akhir_kerjasama=parse_date(row.get('Akhir Kerjasama')) if 'Akhir Kerjasama' in data.columns else None,
                    jenis_kerjasama=row.get('Jenis Kerjasama').lower() if 'Jenis Kerjasama' in data.columns and pd.notna(row.get('Jenis Kerjasama')) else None,
                    jenis_produk=row.get('Jenis Produk').lower() if 'Jenis Produk' in data.columns and pd.notna(row.get('Jenis Produk')) else None,
                    pembayaran=row.get('Pembayaran') if 'Pembayaran' in data.columns and pd.notna(row.get('Pembayaran')) else None,
                    harga_buku=row.get('Harga Buku') if 'Harga Buku' in data.columns and pd.notna(row.get('Harga Buku')) else None,
                    jumlah_komputer=row.get('Jumlah Komputer') if 'Jumlah Komputer' in data.columns and pd.notna(row.get('Jumlah Komputer')) else None,
                    tipe_sekolah=row.get('Tipe Sekolah') if 'Tipe Sekolah' in data.columns and pd.notna(row.get('Tipe Sekolah')) else None,
                    jumlah_siswa_tk=row.get('Jumlah Siswa TK') if 'Jumlah Siswa TK' in data.columns and pd.notna(row.get('Jumlah Siswa TK')) else None,
                    user_produk=user_produk,
                )
                
                # Set jumlah siswa untuk setiap kelas
                for i in range(1, 13):
                    col_name = f'Jumlah Siswa Kelas {i}'
                    if col_name in data.columns:
                        value = row.get(col_name)
                        if pd.notna(value):
                            try:
                                setattr(master_ekskul, f'jumlah_siswa_kelas_{i}', int(value))
                            except (ValueError, TypeError):
                                setattr(master_ekskul, f'jumlah_siswa_kelas_{i}', None)
                        else:
                            setattr(master_ekskul, f'jumlah_siswa_kelas_{i}', None)

                # Set jumlah siswa SMK
                for i in range(10, 13):
                    col_name = f'Jumlah Siswa Kelas {i} SMK'
                    if col_name in data.columns:
                        value = row.get(col_name)
                        if pd.notna(value):
                            try:
                                setattr(master_ekskul, f'jumlah_siswa_kelas_{i}_smk', int(value))
                            except (ValueError, TypeError):
                                setattr(master_ekskul, f'jumlah_siswa_kelas_{i}_smk', None)
                        else:
                            setattr(master_ekskul, f'jumlah_siswa_kelas_{i}_smk', None)
                
                master_ekskul.save()

            except Exception as e:
                logger.error(f"Error pada baris {index + 2}: {str(e)}")
                raise ValidationError(f"Error pada baris {index + 2}: {str(e)}")

        return True, "Data customer ekstrakulikuler berhasil diimpor"
    except pd.errors.ParserError as e:
        logger.error(f"Gagal mengimpor data: Kesalahan format CSV. {str(e)}")
        return False, f"Gagal mengimpor data: Kesalahan format CSV. {str(e)}"
    except Exception as e:
        logger.error(f"Gagal mengimpor data: {str(e)}")
        return False, f"Gagal mengimpor data: {str(e)}"

def func_total_komputer_per_jenjang(daftar_sekolah):
    total_komputer_per_jenjang = {jenjang: 0 for jenjang, _ in JENJANG_CHOICES}
    for sekolah in daftar_sekolah:
        jenjang = sekolah.jenjang
        if jenjang in total_komputer_per_jenjang:
            total_komputer_per_jenjang[jenjang] += sekolah.jumlah_komputer or 0
    return total_komputer_per_jenjang
